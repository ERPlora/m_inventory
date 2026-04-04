"""
Test fixtures for the inventory module.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from inventory.models import Category, InventoryConfig, Product, ProductVariant


@pytest.fixture
def hub_id():
    """Test hub UUID."""
    return uuid.uuid4()


@pytest.fixture
def sample_category(hub_id):
    """Create a sample category (not persisted)."""
    return Category(
        hub_id=hub_id,
        name="Electronics",
        icon="hardware-chip-outline",
        color="#4472C4",
        order=1,
    )


@pytest.fixture
def sample_product(hub_id):
    """Create a sample product (not persisted)."""
    return Product(
        hub_id=hub_id,
        name="Widget Pro",
        sku="WDG-001",
        ean13="1234567890123",
        description="A premium widget",
        product_type="physical",
        price=Decimal("29.99"),
        cost=Decimal("15.00"),
        stock=50,
        low_stock_threshold=10,
    )


@pytest.fixture
def sample_variant(hub_id, sample_product):
    """Create a sample variant (not persisted)."""
    return ProductVariant(
        hub_id=hub_id,
        product_id=sample_product.id or uuid.uuid4(),
        name="Red XL",
        sku="WDG-001-RXL",
        attributes={"color": "red", "size": "XL"},
        price=Decimal("34.99"),
        stock=15,
    )


@pytest.fixture
def sample_config(hub_id):
    """Create a sample config (not persisted)."""
    return InventoryConfig(hub_id=hub_id)
