from decimal import Decimal, ROUND_HALF_UP


def tax_rate_for(amount):
    """Return the tax rate for the given amount.

    Parameters
    ----------
    amount : int | float
        The monetary amount to evaluate.

    Returns
    -------
    float
        0.1 if amount > 1000 else 0.05.
    """
    return 0.1 if amount > 1000 else 0.05


def total_with_tax(amount):
    """Calculate the total including tax, rounded to two decimal places.

    Parameters
    ----------
    amount : int | float
        The base amount before tax.

    Returns
    -------
    float
        The amount plus tax, rounded half‑up to 2 decimal places.
    """
    # Convert inputs to Decimal via string to preserve exact value.
    amt = Decimal(str(amount))
    rate = Decimal(str(tax_rate_for(amount)))
    total = amt + amt * rate
    # Quantize to 2 decimal places using ROUND_HALF_UP to mimic PHP's round.
    rounded_total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(rounded_total)
