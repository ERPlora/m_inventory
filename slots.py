"""
Inventory module slot registrations.

Provides UI extension points for other modules (e.g. POS product cards).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.slots import SlotRegistry

MODULE_ID = "inventory"


def register_slots(slots: SlotRegistry, module_id: str) -> None:
    """
    Register slot content for the inventory module.

    Called by ModuleRuntime during module load.

    Slots this module OFFERS (other modules can inject into):
    - inventory.product_card_badge: Badge on product cards (stock, promo)
    - inventory.product_detail_tabs: Additional tabs in product detail
    - inventory.product_list_filters: Extra filters in product list
    - inventory.category_card_actions: Actions on category cards
    """
    # Inventory does not inject into other modules' slots by default.
    # It provides the slots above for other modules to inject into.
