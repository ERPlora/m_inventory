"""
AI tools for the Inventory module.

Provides create_product, bulk_create_products, create_category,
list_products, and list_categories via @register_tool + AssistantTool.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.ai import AssistantTool, register_tool
from app.core.db.query import HubQuery
from app.core.db.transactions import atomic


def _q(model, session, hub_id):
    return HubQuery(model, session, hub_id)


# ============================================================================
# READ TOOLS
# ============================================================================


@register_tool
class ListProducts(AssistantTool):
    name = "list_products"
    description = (
        "List products in the inventory. Returns id, name, sku, price, stock, and is_active. "
        "Read-only — no side effects. "
        "Use this to browse the catalog or find a product_id before performing other operations."
    )
    module_id = "inventory"
    required_permission = "inventory.view_product"
    parameters = {
        "type": "object",
        "properties": {
            "search": {
                "type": "string",
                "description": "Filter by product name or SKU (case-insensitive partial match).",
            },
            "active_only": {
                "type": "boolean",
                "description": "If true (default), only return active products.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of products to return. Default is 50.",
            },
        },
        "required": [],
        "additionalProperties": False,
    }

    async def execute(self, args: dict, request: Any) -> dict:
        from inventory.models import Product
        from sqlalchemy import or_

        db = request.state.db
        hub_id = request.state.hub_id
        query = _q(Product, db, hub_id)

        if args.get("search"):
            s = args["search"]
            query = query.filter(or_(
                Product.name.ilike(f"%{s}%"),
                Product.sku.ilike(f"%{s}%"),
            ))

        if args.get("active_only", True):
            query = query.filter(Product.is_active == True)  # noqa: E712

        limit = args.get("limit", 50)
        total = await query.count()
        products = await query.order_by(Product.name).limit(limit).all()

        return {
            "products": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "sku": p.sku,
                    "price": str(p.price),
                    "stock": p.stock,
                    "is_active": p.is_active,
                }
                for p in products
            ],
            "total": total,
        }


@register_tool
class ListCategories(AssistantTool):
    name = "list_categories"
    description = (
        "List all product categories. Returns id, name, and product_count. "
        "Read-only — no side effects."
    )
    module_id = "inventory"
    required_permission = "inventory.view_category"
    parameters = {
        "type": "object",
        "properties": {
            "active_only": {
                "type": "boolean",
                "description": "If true (default), only return active categories.",
            },
        },
        "required": [],
        "additionalProperties": False,
    }

    async def execute(self, args: dict, request: Any) -> dict:
        from inventory.models import Category
        from sqlalchemy.orm import selectinload

        db = request.state.db
        hub_id = request.state.hub_id
        query = _q(Category, db, hub_id)

        if args.get("active_only", True):
            query = query.filter(Category.is_active == True)  # noqa: E712

        categories = await query.options(
            selectinload(Category.products)
        ).order_by(Category.order, Category.name).all()

        return {
            "categories": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "product_count": c.product_count,
                }
                for c in categories
            ],
            "total": len(categories),
        }


# ============================================================================
# WRITE TOOLS
# ============================================================================


@register_tool
class CreateProduct(AssistantTool):
    name = "create_product"
    description = (
        "Create a new product in the inventory. "
        "SIDE EFFECT: creates a new product record. Requires confirmation. "
        "name, sku, and price are required. "
        "Use list_products first to check the product does not already exist."
    )
    module_id = "inventory"
    required_permission = "inventory.add_product"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Product name. Required."},
            "sku": {"type": "string", "description": "Stock-keeping unit code. Must be unique. Required."},
            "price": {"type": "number", "description": "Selling price. Required."},
            "description": {"type": "string", "description": "Product description."},
            "product_type": {
                "type": "string",
                "description": "Product type: 'physical' (default) or 'service'.",
            },
            "cost": {"type": "number", "description": "Purchase/cost price. Default is 0."},
            "stock": {"type": "integer", "description": "Initial stock quantity. Default is 0."},
            "ean13": {"type": "string", "description": "EAN-13 barcode (13 digits). Optional."},
            "tax_class_id": {
                "type": "string",
                "description": "Tax class UUID or tax class name (e.g. 'IVA General 21%'). Optional.",
            },
            "is_active": {"type": "boolean", "description": "Whether the product is active. Default is true."},
        },
        "required": ["name", "sku", "price"],
        "additionalProperties": False,
    }

    async def execute(self, args: dict, request: Any) -> dict:
        from inventory.models import Product

        db = request.state.db
        hub_id = request.state.hub_id

        tax_class_id = await _resolve_tax_class(args.get("tax_class_id"), db, hub_id)

        async with atomic(db) as session:
            product = Product(
                hub_id=hub_id,
                name=args["name"],
                sku=args["sku"],
                price=args["price"],
                description=args.get("description", ""),
                product_type=args.get("product_type", "physical"),
                cost=args.get("cost", 0),
                stock=args.get("stock", 0),
                ean13=args.get("ean13") or None,
                tax_class_id=tax_class_id,
                is_active=args.get("is_active", True),
            )
            session.add(product)
            await session.flush()

        return {
            "success": True,
            "product_id": str(product.id),
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price),
        }


@register_tool
class BulkCreateProducts(AssistantTool):
    name = "bulk_create_products"
    description = (
        "Create multiple products at once (max 100). "
        "SIDE EFFECT: creates product records. Requires confirmation. "
        "Each item needs name and price; sku is optional and will be auto-generated if omitted "
        "(format: PROD-001, PROD-002, …). Returns count of created products and any errors."
    )
    module_id = "inventory"
    required_permission = "inventory.add_product"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "description": "List of products to create.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Product name. Required."},
                        "price": {"type": "number", "description": "Selling price. Required."},
                        "sku": {"type": "string", "description": "SKU. Auto-generated if omitted."},
                        "description": {"type": "string"},
                        "product_type": {"type": "string"},
                        "cost": {"type": "number"},
                        "stock": {"type": "integer"},
                        "ean13": {"type": "string"},
                        "tax_class_id": {"type": "string"},
                        "is_active": {"type": "boolean"},
                    },
                    "required": ["name", "price"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["products"],
        "additionalProperties": False,
    }

    async def execute(self, args: dict, request: Any) -> dict:
        from inventory.models import Product

        db = request.state.db
        hub_id = request.state.hub_id
        items = args["products"]
        created = []
        errors = []

        async with atomic(db) as session:
            # Count existing products to avoid SKU collisions when auto-generating
            from sqlalchemy import func, select as sa_select
            from inventory.models import Product as _Product
            existing_count_result = await session.execute(
                sa_select(func.count()).select_from(_Product).where(_Product.hub_id == hub_id)
            )
            existing_count = existing_count_result.scalar_one()

            for i, item in enumerate(items):
                try:
                    sku = item.get("sku") or f"PROD-{(existing_count + i + 1):03d}"
                    tax_class_id = await _resolve_tax_class(
                        item.get("tax_class_id"), session, hub_id
                    )
                    product = Product(
                        hub_id=hub_id,
                        name=item["name"],
                        sku=sku,
                        price=item["price"],
                        description=item.get("description", ""),
                        product_type=item.get("product_type", "physical"),
                        cost=item.get("cost", 0),
                        stock=item.get("stock", 0),
                        ean13=item.get("ean13") or None,
                        tax_class_id=tax_class_id,
                        is_active=item.get("is_active", True),
                    )
                    session.add(product)
                    created.append({"name": item["name"], "sku": sku})
                except Exception as e:
                    errors.append({"index": i, "name": item.get("name", ""), "error": str(e)})
            await session.flush()

        return {
            "created": len(created),
            "errors": len(errors),
            "details": {"created": created, "errors": errors},
        }


@register_tool
class CreateCategory(AssistantTool):
    name = "create_category"
    description = (
        "Create a new product category. "
        "SIDE EFFECT: creates a new category record. Requires confirmation. "
        "Only name is required. "
        "Use list_categories first to check the category does not already exist."
    )
    module_id = "inventory"
    required_permission = "inventory.add_category"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Category name. Required."},
            "slug": {"type": "string", "description": "URL-friendly slug. Auto-generated from name if omitted."},
            "icon": {"type": "string", "description": "Ionicon name (e.g. 'cube-outline'). Default: 'cube-outline'."},
            "color": {"type": "string", "description": "Hex color code (e.g. '#3880ff'). Default: '#3880ff'."},
            "description": {"type": "string", "description": "Category description."},
            "order": {"type": "integer", "description": "Display order (lower = first). Default is 0."},
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    async def execute(self, args: dict, request: Any) -> dict:
        from inventory.models import Category

        db = request.state.db
        hub_id = request.state.hub_id

        name = args["name"]
        slug = args.get("slug") or _slugify(name)

        async with atomic(db) as session:
            category = Category(
                hub_id=hub_id,
                name=name,
                slug=slug,
                icon=args.get("icon", "cube-outline"),
                color=args.get("color", "#3880ff"),
                description=args.get("description", ""),
                order=args.get("order", 0),
            )
            session.add(category)
            await session.flush()

        return {
            "success": True,
            "category_id": str(category.id),
            "name": category.name,
            "slug": category.slug,
        }


# ============================================================================
# Helpers
# ============================================================================


def _slugify(text: str) -> str:
    """Simple slug generator: lowercase, replace spaces/special chars with hyphens."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug


async def _resolve_tax_class(
    value: str | None, session: Any, hub_id: uuid.UUID
) -> uuid.UUID | None:
    """
    Resolve a tax_class_id argument to a UUID.

    Accepts:
    - None / empty → returns None
    - A valid UUID string → returns the UUID directly
    - A name string → looks up TaxClass by name and returns its id
    """
    if not value:
        return None

    # Try parsing as UUID first
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        pass

    # Fall back to name lookup
    try:
        from app.apps.configuration.models import TaxClass
        query = HubQuery(TaxClass, session, hub_id)
        tc = await query.filter(TaxClass.name == value, TaxClass.is_active == True).first()  # noqa: E712
        if tc:
            return tc.id
    except Exception:
        pass

    return None
