"""
Inventory module REST API -- FastAPI router.

JSON endpoints for external consumers (Cloud sync, CLI, webhooks).
Mounted at /api/v1/m/inventory/ by ModuleRuntime.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import selectinload

from app.core.db.query import HubQuery
from app.core.db.transactions import atomic
from app.core.dependencies import CurrentUser, DbSession, HubId

from .models import Category, Product
from .schemas import ProductCreate, ProductUpdate

api_router = APIRouter()


def _q(model, session, hub_id):
    return HubQuery(model, session, hub_id)


@api_router.get("/products")
async def list_products(
    request: Request, db: DbSession, hub_id: HubId,
    q: str = "", offset: int = 0, limit: int = Query(default=20, le=100),
):
    """List products with search."""
    from sqlalchemy import or_

    query = _q(Product, db, hub_id).filter(Product.is_active == True)  # noqa: E712
    if q:
        query = query.filter(or_(
            Product.name.ilike(f"%{q}%"),
            Product.sku.ilike(f"%{q}%"),
        ))

    total = await query.count()
    products = await query.options(
        selectinload(Product.categories),
    ).order_by(Product.name).offset(offset).limit(limit).all()

    return {
        "products": [{
            "id": str(p.id), "name": p.name, "sku": p.sku,
            "price": str(p.price), "cost": str(p.cost),
            "stock": p.stock, "product_type": p.product_type,
            "is_active": p.is_active,
            "categories": [{"id": str(c.id), "name": c.name} for c in p.categories],
            "created_at": p.created_at.isoformat(),
        } for p in products],
        "total": total,
    }


@api_router.get("/products/{product_id}")
async def get_product(
    product_id: uuid.UUID, request: Request, db: DbSession, hub_id: HubId,
):
    """Get product details."""
    product = await _q(Product, db, hub_id).options(
        selectinload(Product.categories),
        selectinload(Product.variants),
    ).get(product_id)
    if product is None:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    return {
        "id": str(product.id), "name": product.name, "sku": product.sku,
        "ean13": product.ean13, "description": product.description,
        "product_type": product.product_type,
        "price": str(product.price), "cost": str(product.cost),
        "stock": product.stock, "low_stock_threshold": product.low_stock_threshold,
        "is_active": product.is_active,
        "categories": [{"id": str(c.id), "name": c.name} for c in product.categories],
        "variants": [{
            "id": str(v.id), "name": v.name, "sku": v.sku,
            "price": str(v.price), "stock": v.stock,
        } for v in product.variants],
        "created_at": product.created_at.isoformat(),
    }


@api_router.post("/products")
async def create_product(
    request: Request, body: ProductCreate,
    db: DbSession, user: CurrentUser, hub_id: HubId,
):
    """Create a product."""
    async with atomic(db) as session:
        product = Product(
            hub_id=hub_id,
            **body.model_dump(exclude={"category_names"}),
        )
        session.add(product)
        await session.flush()

        if body.category_names:
            cats = await _q(Category, session, hub_id).filter(
                Category.name.in_(body.category_names)
            ).all()
            product.categories = cats

    return JSONResponse(
        {"id": str(product.id), "name": product.name, "created": True},
        status_code=201,
    )


@api_router.patch("/products/{product_id}")
async def update_product(
    product_id: uuid.UUID, body: ProductUpdate,
    request: Request, db: DbSession, user: CurrentUser, hub_id: HubId,
):
    """Update a product."""
    product = await _q(Product, db, hub_id).get(product_id)
    if product is None:
        return JSONResponse({"error": "Product not found"}, status_code=404)

    for key, value in body.model_dump(exclude_unset=True, exclude={"category_names"}).items():
        setattr(product, key, value)

    if body.category_names is not None:
        cats = await _q(Category, db, hub_id).filter(
            Category.name.in_(body.category_names)
        ).all()
        product.categories = cats

    await db.flush()
    return {"id": str(product.id), "name": product.name, "updated": True}


@api_router.delete("/products/{product_id}")
async def delete_product(
    product_id: uuid.UUID, request: Request,
    db: DbSession, user: CurrentUser, hub_id: HubId,
):
    """Soft-delete a product."""
    deleted = await _q(Product, db, hub_id).delete(product_id)
    if not deleted:
        return JSONResponse({"error": "Product not found"}, status_code=404)
    return {"deleted": True}


# ============================================================================
# Categories API
# ============================================================================

@api_router.get("/categories")
async def list_categories(
    request: Request, db: DbSession, hub_id: HubId,
    offset: int = 0, limit: int = Query(default=50, le=200),
):
    """List categories."""
    cats = await _q(Category, db, hub_id).filter(
        Category.is_active == True  # noqa: E712
    ).order_by(Category.order, Category.name).offset(offset).limit(limit).all()

    return {
        "categories": [{
            "id": str(c.id), "name": c.name, "icon": c.icon,
            "color": c.color, "order": c.order,
        } for c in cats],
    }
