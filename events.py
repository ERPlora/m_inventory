"""
Inventory module event subscriptions.

Registers handlers on the AsyncEventBus during module load.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.events.bus import AsyncEventBus

logger = logging.getLogger(__name__)

MODULE_ID = "inventory"


async def register_events(bus: AsyncEventBus, module_id: str) -> None:
    """
    Register event handlers for the inventory module.

    Called by ModuleRuntime during module load.
    """

    # Listen for stock changes from sales module
    await bus.subscribe("sales.completed", _on_sale_completed, module_id=module_id)
    await bus.subscribe("inventory.stock_changed", _check_low_stock, module_id=module_id)


async def _on_sale_completed(
    event: str, sender: object = None, sale: object = None,
    session: object = None, **kwargs: object,
) -> None:
    """Reduce stock when a sale is completed."""
    if sale is None:
        return

    items = getattr(sale, "items", [])
    for item in items:
        product = getattr(item, "product", None)
        if product is None:
            continue
        # Only reduce stock for physical products
        if getattr(product, "product_type", "physical") == "physical":
            qty = getattr(item, "quantity", 1)
            product.stock = max(0, product.stock - qty)

    if session is not None:
        try:
            await session.flush()
        except Exception:
            logger.exception("Failed to update stock after sale")


async def _check_low_stock(
    event: str, sender: object = None, product: object = None, **kwargs: object,
) -> None:
    """Check if stock has fallen below threshold and log warning."""
    if product is None:
        return

    stock = getattr(product, "stock", 0)
    threshold = getattr(product, "low_stock_threshold", 0)

    if stock <= threshold:
        logger.warning(
            "Low stock alert: product %s (%s) has %d units (threshold: %d)",
            getattr(product, "name", "?"),
            getattr(product, "id", "?"),
            stock,
            threshold,
        )
