"""
Tests for inventory module models.
"""

from __future__ import annotations

from decimal import Decimal

from inventory.models import Category, Product


class TestProduct:
    def test_is_low_stock_true(self, sample_product):
        sample_product.stock = 5
        sample_product.low_stock_threshold = 10
        assert sample_product.is_low_stock is True

    def test_is_low_stock_false(self, sample_product):
        sample_product.stock = 50
        sample_product.low_stock_threshold = 10
        assert sample_product.is_low_stock is False

    def test_is_low_stock_equal(self, sample_product):
        sample_product.stock = 10
        sample_product.low_stock_threshold = 10
        assert sample_product.is_low_stock is True

    def test_profit_margin_with_cost(self, sample_product):
        sample_product.price = Decimal("30.00")
        sample_product.cost = Decimal("20.00")
        assert sample_product.profit_margin == 50.0

    def test_profit_margin_zero_cost(self, sample_product):
        sample_product.cost = Decimal("0.00")
        assert sample_product.profit_margin == 0.0

    def test_is_service_false(self, sample_product):
        sample_product.product_type = "physical"
        assert sample_product.is_service is False

    def test_is_service_true(self, sample_product):
        sample_product.product_type = "service"
        assert sample_product.is_service is True

    def test_get_initial(self, sample_product):
        assert sample_product.get_initial() == "W"

    def test_get_initial_empty(self, hub_id):
        p = Product(hub_id=hub_id, name="", sku="X", price=Decimal("1.00"))
        assert p.get_initial() == "?"

    def test_get_image_path_default(self, sample_product):
        sample_product.image = ""
        assert "placeholder" in sample_product.get_image_path()

    def test_get_image_path_with_image(self, sample_product):
        sample_product.image = "/media/products/test.jpg"
        assert sample_product.get_image_path() == "/media/products/test.jpg"

    def test_repr(self, sample_product):
        assert "Widget Pro" in repr(sample_product)
        assert "WDG-001" in repr(sample_product)


class TestCategory:
    def test_get_initial(self, sample_category):
        assert sample_category.get_initial() == "E"

    def test_get_initial_empty(self, hub_id):
        c = Category(hub_id=hub_id, name="")
        assert c.get_initial() == "?"

    def test_get_image_url_empty(self, sample_category):
        sample_category.image = ""
        assert sample_category.get_image_url() is None

    def test_get_image_url_with_image(self, sample_category):
        sample_category.image = "/media/categories/test.jpg"
        assert sample_category.get_image_url() == "/media/categories/test.jpg"

    def test_repr(self, sample_category):
        assert "Electronics" in repr(sample_category)


class TestProductVariant:
    def test_repr(self, sample_variant):
        assert "Red XL" in repr(sample_variant)


class TestInventoryConfig:
    def test_defaults(self, sample_config):
        assert sample_config.allow_negative_stock is False
        assert sample_config.low_stock_alert_enabled is True
        assert sample_config.auto_generate_sku is True
        assert sample_config.barcode_enabled is True

    def test_repr(self, sample_config):
        assert "InventoryConfig" in repr(sample_config)
