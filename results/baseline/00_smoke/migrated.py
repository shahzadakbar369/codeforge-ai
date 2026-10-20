from decimal import Decimal, ROUND_HALF_UP

def calculate_invoice(subtotal, tax_rate, discount):
    """Calculate the invoice total.

    Parameters
    ----------
    subtotal : float | int
        The pre‑tax subtotal amount.
    tax_rate : float | int
        The tax rate expressed as a decimal (e.g., 0.07 for 7%).
    discount : float | int
        The discount to subtract from the subtotal.

    Returns
    -------
    float
        The total amount including tax, rounded to two decimal places using
        half‑up rounding (mirroring PHP's round behaviour).
    """
    # Convert inputs to Decimal for accurate arithmetic and half‑up rounding.
    # Using str() avoids binary floating‑point representation errors.
    subtotal_dec = Decimal(str(subtotal))
    tax_rate_dec = Decimal(str(tax_rate))
    discount_dec = Decimal(str(discount))

    # Subtract discount and clamp to zero if negative.
    total = subtotal_dec - discount_dec
    if total < 0:
        total = Decimal('0')

    # Apply tax: total + (total * tax_rate)
    total = total + (total * tax_rate_dec)

    # Round to two decimal places using half‑up (PHP round behaviour).
    rounded_total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return float(rounded_total)
