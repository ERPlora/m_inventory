"""
Inventory module hook registrations.

Registers actions and filters on the HookRegistry during module load.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.hooks.registry import HookRegistry

MODULE_ID = "inventory"


def register_hooks(hooks: HookRegistry, module_id: str) -> None:
    """
    Register hooks for the inventory module.

    Called by ModuleRuntime during module load.

    Hooks this module OFFERS:
    - inventory.before_stock_change: validate/block stock changes
    - inventory.after_stock_change: react to stock changes
    - inventory.filter_product_data: modify product data before save
    - inventory.filter_product_list: modify product list queries
    """
    # No hooks consumed from other modules in the base inventory.
    # Other modules can hook INTO inventory via:
    #   hooks.add_action("inventory.before_stock_change", callback, module_id="other_module")
    #   hooks.add_filter("inventory.filter_product_list", callback, module_id="other_module")
