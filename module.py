"""
Inventory module manifest.

Product and stock management with categories, variants, barcodes, import/export.
"""


# ---------------------------------------------------------------------------
# Module identity
# ---------------------------------------------------------------------------
MODULE_ID = "inventory"
MODULE_NAME = "Inventory"
MODULE_VERSION = "1.0.6"
MODULE_ICON = "cube-outline"
MODULE_DESCRIPTION = "Product and stock management with categories, variants, barcodes, import/export"
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
    "label": "Inventory",
    "icon": "cube-outline",
    "order": 10,
}

# ---------------------------------------------------------------------------
# Navigation tabs (bottom tabbar in module views)
# ---------------------------------------------------------------------------
NAVIGATION = [
    {
        "id": "dashboard",
        "label": "Overview",
        "icon": "grid-outline",
        "view": "",
    },
    {
        "id": "products",
        "label": "Products",
        "icon": "cube-outline",
        "view": "products",
    },
    {
        "id": "categories",
        "label": "Categories",
        "icon": "albums-outline",
        "view": "categories",
    },
    {
        "id": "reports",
        "label": "Reports",
        "icon": "stats-chart-outline",
        "view": "reports",
    },
    {
        "id": "settings",
        "label": "Settings",
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
    ("view_product", "View products"),
    ("add_product", "Add products"),
    ("change_product", "Edit products"),
    ("delete_product", "Delete products"),
    ("view_category", "View categories"),
    ("add_category", "Add categories"),
    ("change_category", "Edit categories"),
    ("delete_category", "Delete categories"),
    ("export_product", "Export products"),
    ("import_product", "Import products"),
    ("manage_settings", "Manage settings"),
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
