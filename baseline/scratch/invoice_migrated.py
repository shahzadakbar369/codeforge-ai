def calculate_invoice(subtotal, tax_rate, discount):
    from decimal import Decimal, ROUND_HALF_UP
    subtotal = Decimal(str(subtotal))
    tax_rate = Decimal(str(tax_rate))
    discount = Decimal(str(discount))
    total = subtotal - discount
    if total < 0:
        total = Decimal('0')
    total = total + (total * tax_rate)
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(total)

if __name__ == "__main__":
    print(calculate_invoice(100, 0.17, 10))