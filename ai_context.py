"""
AI context for the inventory module.

Provides structured context for the AI assistant about this module's
models, workflows, and business rules.
"""

CONTEXT = """
## Inventory Module

Product and stock management with categories, variants, barcodes, and import/export.
Used by retail, wholesale, restaurants, bars, cafes, beauty, and manufacturing sectors.

### Models
- InventoryConfig: singleton per hub — allow_negative_stock, low_stock_alert_enabled, auto_generate_sku, barcode_enabled
- Category: name, slug, icon, color, image, description, order, tax_class_id, is_active
- Product: name, sku (unique), ean13 (unique, 13 digits), description, product_type (physical/service), price, cost, stock, low_stock_threshold, tax_class_id, is_active
- ProductVariant: product_id (FK), name, sku (unique), attributes (JSONB), price, stock, image, is_active
- product_category_m2m: many-to-many between Product and Category

### Key Workflows
- List products: use list_products (filter by name/SKU, active_only=true by default)
- List categories: use list_categories
- Create product: use create_product (name + sku + price required; check duplicates first with list_products)
- Bulk create: use bulk_create_products (up to 100 items; sku auto-generated as PROD-001 if omitted)
- Create category: use create_category (name required; check duplicates first with list_categories)
- tax_class_id: accepts UUID or name string (e.g. "IVA General 21%") — resolved automatically

### Dependencies
- Requires: none

### Business Rules
- SKU must be unique per hub; EAN-13 must be unique per hub if provided
- Variants inherit low_stock_threshold from parent product
- product_type is "physical" (tracks stock) or "service" (no physical stock)
- allow_negative_stock setting controls whether stock can go below 0
- low_stock_alert fires when stock <= low_stock_threshold (default 10)
- Before creating a product, always call list_products to verify it doesn't already exist
- Before creating a category, always call list_categories to verify it doesn't already exist
"""

SOPS = [
    {
        "id": "list_products",
        "triggers_es": ["listar productos", "ver productos", "cuantos productos", "catalogo"],
        "triggers_en": ["list products", "show products", "how many products", "catalog"],
        "steps": ["list_products"],
        "modules_required": ["inventory"],
    },
    {
        "id": "create_product",
        "triggers_es": ["crear producto", "añadir producto", "nuevo producto", "agregar producto"],
        "triggers_en": ["create product", "add product", "new product"],
        "steps": ["list_products", "create_product"],
        "modules_required": ["inventory"],
    },
    {
        "id": "bulk_create_products",
        "triggers_es": ["crear varios productos", "importar productos", "cargar productos en masa"],
        "triggers_en": ["bulk create products", "create multiple products", "import products"],
        "steps": ["bulk_create_products"],
        "modules_required": ["inventory"],
    },
    {
        "id": "create_category",
        "triggers_es": ["crear categoría", "añadir categoría", "nueva categoría"],
        "triggers_en": ["create category", "add category", "new category"],
        "steps": ["list_categories", "create_category"],
        "modules_required": ["inventory"],
    },
]
