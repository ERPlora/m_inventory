"""
Inventory module models -- SQLAlchemy 2.0.

Models: InventoryConfig, Category, Product, ProductVariant.
M2M: product_category_m2m (Product <-> Category).
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HubBaseModel

if TYPE_CHECKING:
    pass


# ============================================================================
# M2M association table: Product <-> Category
# ============================================================================

product_category_m2m = Table(
    "inventory_product_categories",
    HubBaseModel.metadata,
    Column("product_id", Uuid, ForeignKey("inventory_product.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Uuid, ForeignKey("inventory_category.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================================
# Inventory Config (singleton per hub)
# ============================================================================

class InventoryConfig(HubBaseModel):
    """Singleton configuration for the inventory module."""

    __tablename__ = "inventory_config"

    allow_negative_stock: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false",
    )
    low_stock_alert_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true",
    )
    auto_generate_sku: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true",
    )
    barcode_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true",
    )

    def __repr__(self) -> str:
        return "<InventoryConfig>"


# ============================================================================
# Category
# ============================================================================

class Category(HubBaseModel):
    """Product category with optional image, icon, and color."""

    __tablename__ = "inventory_category"
    __table_args__ = (
        Index("ix_inventory_category_order", "hub_id", "order"),
        Index("ix_inventory_category_active", "hub_id", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), default="", server_default="")
    icon: Mapped[str] = mapped_column(String(50), default="cube-outline", server_default="cube-outline")
    color: Mapped[str] = mapped_column(String(7), default="#3880ff", server_default="#3880ff")
    image: Mapped[str] = mapped_column(String(500), default="", server_default="")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    tax_class_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("configuration_taxclass.id", ondelete="SET NULL"), nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    products: Mapped[list[Product]] = relationship(
        "Product", secondary=product_category_m2m, back_populates="categories",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name!r}>"

    @property
    def product_count(self) -> int:
        """Count of active products. Works on eagerly loaded collections."""
        return len([p for p in self.products if p.is_active]) if self.products else 0

    def get_image_url(self) -> str | None:
        return self.image if self.image else None

    def get_initial(self) -> str:
        if self.name:
            return self.name[0].upper()
        return "?"


# ============================================================================
# Product
# ============================================================================

PRODUCT_TYPE_CHOICES = ("physical", "service")


class Product(HubBaseModel):
    """Product with price, cost, stock, variants, and barcode support."""

    __tablename__ = "inventory_product"
    __table_args__ = (
        Index("ix_inventory_product_sku", "hub_id", "sku", unique=True),
        Index("ix_inventory_product_name", "hub_id", "name"),
        Index("ix_inventory_product_ean13", "hub_id", "ean13", unique=True),
        Index("ix_inventory_product_active", "hub_id", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    ean13: Mapped[str | None] = mapped_column(String(13), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    product_type: Mapped[str] = mapped_column(
        String(20), default="physical", server_default="physical",
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False,
    )
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), server_default="0.00",
    )
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10, server_default="10")
    tax_class_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("configuration_taxclass.id", ondelete="SET NULL"), nullable=True,
    )
    image: Mapped[str] = mapped_column(String(500), default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    categories: Mapped[list[Category]] = relationship(
        "Category", secondary=product_category_m2m, back_populates="products",
    )
    variants: Mapped[list[ProductVariant]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Product {self.name!r} ({self.sku})>"

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.low_stock_threshold

    @property
    def profit_margin(self) -> float:
        if self.cost and self.cost > 0:
            return float(((self.price - self.cost) / self.cost) * 100)
        return 0.0

    @property
    def is_service(self) -> bool:
        return self.product_type == "service"

    def get_image_path(self) -> str:
        if self.image:
            return self.image
        return "/static/products/images/placeholder.png"

    def get_initial(self) -> str:
        if self.name:
            return self.name[0].upper()
        return "?"


# ============================================================================
# Product Variant
# ============================================================================

class ProductVariant(HubBaseModel):
    """Variant of a product (color, size, weight, etc.) with independent stock."""

    __tablename__ = "inventory_product_variant"
    __table_args__ = (
        UniqueConstraint("hub_id", "product_id", "name", name="uq_inventory_variant_product_name"),
        Index("ix_inventory_variant_sku", "hub_id", "sku", unique=True),
        Index("ix_inventory_variant_product_active", "hub_id", "product_id", "is_active"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("inventory_product.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    image: Mapped[str] = mapped_column(String(500), default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="variants")

    def __repr__(self) -> str:
        return f"<ProductVariant {self.name!r} of product={self.product_id}>"

    @property
    def is_low_stock(self) -> bool:
        """Uses parent product's threshold."""
        if self.product:
            return self.stock <= self.product.low_stock_threshold
        return False
