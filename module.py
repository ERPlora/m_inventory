"""
Inventory module manifest.

Product and stock management with categories, variants, barcodes, import/export.
"""

from app.core.i18n import LazyString

# ---------------------------------------------------------------------------
# Module identity
# ---------------------------------------------------------------------------
MODULE_ID = "inventory"
MODULE_NAME = LazyString("Inventory", module_id="inventory")
MODULE_VERSION = "1.0.0"
MODULE_ICON = "cube-outline"
MODULE_DESCRIPTION = LazyString(
    "Product and stock management with categories, variants, barcodes, import/export",
    module_id="inventory",
)
MODULE_AUTHOR = "ERPlora"
MODULE_CATEGORY = "inventory"

# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------
HAS_MODELS = True
MIDDLEWARE = ""

# ---------------------------------------------------------------------------
# Target Industries
# ---------------------------------------------------------------------------
MODULE_INDUSTRIES = [
    "retail",
    "wholesale",
    "restaurant",
    "bar",
    "cafe",
    "fast_food",
    "beauty",
    "manufacturing",
]

# ---------------------------------------------------------------------------
# Menu (sidebar entry)
# ---------------------------------------------------------------------------
MENU = {
    "label": LazyString("Inventory", module_id="inventory"),
    "icon": "cube-outline",
    "order": 10,
}

# ---------------------------------------------------------------------------
# Navigation tabs (bottom tabbar in module views)
# ---------------------------------------------------------------------------
NAVIGATION = [
    {
        "id": "dashboard",
        "label": LazyString("Overview", module_id="inventory"),
        "icon": "grid-outline",
        "view": "",
    },
    {
        "id": "products",
        "label": LazyString("Products", module_id="inventory"),
        "icon": "cube-outline",
        "view": "products",
    },
    {
        "id": "categories",
        "label": LazyString("Categories", module_id="inventory"),
        "icon": "albums-outline",
        "view": "categories",
    },
    {
        "id": "reports",
        "label": LazyString("Reports", module_id="inventory"),
        "icon": "stats-chart-outline",
        "view": "reports",
    },
    {
        "id": "settings",
        "label": LazyString("Settings", module_id="inventory"),
        "icon": "settings-outline",
        "view": "settings",
    },
]

# ---------------------------------------------------------------------------
# Dependencies (other modules required to be active)
# ---------------------------------------------------------------------------
DEPENDENCIES: list[str] = []

# ---------------------------------------------------------------------------
# Settings (defaults)
# ---------------------------------------------------------------------------
SETTINGS = {
    "allow_negative_stock": False,
    "low_stock_alert_enabled": True,
    "items_per_page": 20,
}

# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------
PERMISSIONS = [
    ("view_product", LazyString("View products", module_id="inventory")),
    ("add_product", LazyString("Add products", module_id="inventory")),
    ("change_product", LazyString("Edit products", module_id="inventory")),
    ("delete_product", LazyString("Delete products", module_id="inventory")),
    ("view_category", LazyString("View categories", module_id="inventory")),
    ("add_category", LazyString("Add categories", module_id="inventory")),
    ("change_category", LazyString("Edit categories", module_id="inventory")),
    ("delete_category", LazyString("Delete categories", module_id="inventory")),
    ("export_product", LazyString("Export products", module_id="inventory")),
    ("import_product", LazyString("Import products", module_id="inventory")),
    ("manage_settings", LazyString("Manage settings", module_id="inventory")),
]

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": [
        "view_product", "add_product", "change_product", "delete_product",
        "view_category", "add_category", "change_category", "delete_category",
        "export_product", "import_product", "manage_settings",
    ],
    "employee": ["view_product", "view_category"],
}

# ---------------------------------------------------------------------------
# Scheduled tasks
# ---------------------------------------------------------------------------
SCHEDULED_TASKS: list[dict] = []

# ---------------------------------------------------------------------------
# Pricing (free module)
# ---------------------------------------------------------------------------
# PRICING = {"monthly": 0, "yearly": 0}
