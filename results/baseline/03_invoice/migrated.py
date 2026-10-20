import math
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(value, ndigits=0):
    """Round a number to ``ndigits`` places using half‑up rounding.
    This mimics PHP's round() function which rounds half values away from zero.
    """
    d = Decimal(str(value))
    quant = Decimal('1e-' + str(ndigits))
    return float(d.quantize(quant, rounding=ROUND_HALF_UP))


def line_total(price, qty, discount_percent=0):
    total = price * qty
    total -= total * discount_percent / 100
    return round_half_up(total, 2)


def invoice_subtotal(items):
    sum_ = 0
    for item in items:
        discount = item.get("discount", 0)
        sum_ += line_total(item["price"], item["qty"], discount)
    return round_half_up(sum_, 2)


def tax_for_amount(amount):
    if amount <= 1000:
        rate = 0.05
    elif amount <= 5000:
        rate = 0.10
    else:
        rate = 0.15
    return round_half_up(amount * rate, 2)


def shipping_cost(weight_kg):
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    if weight_kg <= 1:
        return 5
    if weight_kg <= 5:
        return 12.5
    if weight_kg <= 20:
        return 25
    return 25 + math.ceil((weight_kg - 20) / 10) * 8


def late_fee(amount, days_late):
    if days_late <= 0:
        return 0
    fee = amount * 0.015 * math.ceil(days_late / 30)
    return round_half_up(min(fee, amount * 0.25), 2)


def format_invoice_number(n):
    return f"INV-{int(n):05d}"


def invoice_total(items, shipping_weight):
    sub = invoice_subtotal(items)
    tax = tax_for_amount(sub)
    ship = shipping_cost(shipping_weight)
    return round_half_up(sub + tax + ship, 2)


def split_payment(total, installments):
    if installments < 1:
        raise ValueError("Need at least one installment")
    base = math.floor(total * 100 / installments) / 100
    payments = [base] * installments
    remainder = round_half_up(total - base * installments, 2)
    payments[-1] = round_half_up(payments[-1] + remainder, 2)
    return payments