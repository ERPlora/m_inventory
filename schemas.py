"""
Pydantic schemas for inventory module.

Replaces Django forms -- used for request validation.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


# ============================================================================
# Product
# ============================================================================

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    ean13: str | None = Field(default=None, max_length=13)
    description: str = ""
    product_type: str = Field(default="physical", pattern="^(physical|service)$")
    price: Decimal = Field(ge=Decimal("0.01"))
    cost: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    stock: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    tax_class_id: uuid.UUID | None = None
    category_names: list[str] = []


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    ean13: str | None = Field(default=None, max_length=13)
    description: str | None = None
    product_type: str | None = None
    price: Decimal | None = None
    cost: Decimal | None = None
    stock: int | None = None
    low_stock_threshold: int | None = None
    tax_class_id: uuid.UUID | None = None
    category_names: list[str] | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    sku: str
    ean13: str | None
    description: str
    product_type: str
    price: Decimal
    cost: Decimal
    stock: int
    low_stock_threshold: int
    is_active: bool
    image: str

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int


# ============================================================================
# Category
# ============================================================================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    icon: str = Field(default="cube-outline", max_length=50)
    color: str = Field(default="#3880ff", max_length=7)
    order: int = Field(default=0, ge=0)
    tax_class_id: uuid.UUID | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    order: int | None = None
    tax_class_id: uuid.UUID | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    icon: str
    color: str
    order: int
    is_active: bool

    model_config = {"from_attributes": True}


# ============================================================================
# Inventory Config
# ============================================================================

class InventoryConfigUpdate(BaseModel):
    allow_negative_stock: bool | None = None
    low_stock_alert_enabled: bool | None = None
    auto_generate_sku: bool | None = None
    barcode_enabled: bool | None = None


# ============================================================================
# Import result
# ============================================================================

class ImportResult(BaseModel):
    success: bool
    message: str
    created: int = 0
    updated: int = 0
    errors: list[str] = []
