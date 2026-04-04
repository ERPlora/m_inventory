"""
Barcode Generation Utilities for Inventory Module.

Supports Code128 (SKU) and EAN-13 barcode formats as SVG.
"""

import io

import barcode
from barcode.writer import SVGWriter


def generate_barcode_svg(sku: str, format_type: str = "code128") -> str:
    """
    Generate a barcode in SVG format from SKU.

    Args:
        sku: Product SKU to encode.
        format_type: Barcode format ('code128' or 'ean13').

    Returns:
        SVG content as string.

    Raises:
        ValueError: If SKU is invalid for selected format.
    """
    try:
        if format_type.lower() == "code128":
            barcode_class = barcode.get_barcode_class("code128")
        elif format_type.lower() == "ean13":
            barcode_class = barcode.get_barcode_class("ean13")
            if not sku.isdigit() or len(sku) not in (12, 13):
                raise ValueError("EAN13 requires 12 or 13 digits")
        else:
            raise ValueError(f"Unsupported barcode format: {format_type}")

        output = io.BytesIO()
        barcode_instance = barcode_class(sku, writer=SVGWriter())
        barcode_instance.write(output, {
            "module_width": 0.3,
            "module_height": 10,
            "font_size": 10,
            "text_distance": 5,
            "quiet_zone": 6.5,
        })

        output.seek(0)
        return output.read().decode("utf-8")

    except Exception as e:
        raise ValueError(f"Error generating barcode: {e!s}") from e


def is_valid_sku_for_barcode(sku: str, format_type: str = "code128") -> tuple[bool, str]:
    """
    Validate if SKU can be encoded in specified barcode format.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not sku or not sku.strip():
        return False, "SKU cannot be empty"

    sku = sku.strip()

    if format_type.lower() == "code128":
        if len(sku) > 80:
            return False, "SKU too long for Code128 (max 80 characters)"
        return True, ""

    if format_type.lower() == "ean13":
        if not sku.isdigit():
            return False, "EAN13 requires only digits"
        if len(sku) not in (12, 13):
            return False, "EAN13 requires 12 or 13 digits"
        return True, ""

    return False, f"Unsupported format: {format_type}"
