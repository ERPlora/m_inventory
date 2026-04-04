"""Initial inventory module tables.

Revision ID: 001
Create Date: 2026-04-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # inventory_config
    op.create_table(
        "inventory_config",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("hub_id", UUID(as_uuid=True), nullable=False),
        sa.Column("allow_negative_stock", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("low_stock_alert_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("auto_generate_sku", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("barcode_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # inventory_category
    op.create_table(
        "inventory_category",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("hub_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), server_default="", nullable=False),
        sa.Column("icon", sa.String(50), server_default="cube-outline", nullable=False),
        sa.Column("color", sa.String(7), server_default="#3880ff", nullable=False),
        sa.Column("image", sa.String(500), server_default="", nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tax_class_id", UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_category_order", "inventory_category", ["hub_id", "order"])
    op.create_index("ix_inventory_category_active", "inventory_category", ["hub_id", "is_active"])

    # inventory_product
    op.create_table(
        "inventory_product",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("hub_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("ean13", sa.String(13), nullable=True),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("product_type", sa.String(20), server_default="physical", nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("low_stock_threshold", sa.Integer(), server_default="10", nullable=False),
        sa.Column("tax_class_id", UUID(as_uuid=True), nullable=True),
        sa.Column("image", sa.String(500), server_default="", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_product_sku", "inventory_product", ["hub_id", "sku"], unique=True)
    op.create_index("ix_inventory_product_name", "inventory_product", ["hub_id", "name"])
    op.create_index("ix_inventory_product_ean13", "inventory_product", ["hub_id", "ean13"], unique=True)
    op.create_index("ix_inventory_product_active", "inventory_product", ["hub_id", "is_active"])

    # inventory_product_categories (M2M)
    op.create_table(
        "inventory_product_categories",
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("inventory_product.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", UUID(as_uuid=True), sa.ForeignKey("inventory_category.id", ondelete="CASCADE"), primary_key=True),
    )

    # inventory_product_variant
    op.create_table(
        "inventory_product_variant",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("hub_id", UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("inventory_product.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("attributes", JSONB(), server_default="{}", nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("image", sa.String(500), server_default="", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_variant_sku", "inventory_product_variant", ["hub_id", "sku"], unique=True)
    op.create_index("ix_inventory_variant_product_active", "inventory_product_variant", ["hub_id", "product_id", "is_active"])
    op.create_unique_constraint(
        "uq_inventory_variant_product_name",
        "inventory_product_variant",
        ["hub_id", "product_id", "name"],
    )


def downgrade() -> None:
    op.drop_table("inventory_product_variant")
    op.drop_table("inventory_product_categories")
    op.drop_table("inventory_product")
    op.drop_table("inventory_category")
    op.drop_table("inventory_config")
