from decimal import Decimal, ROUND_HALF_UP

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

def modulo(a, b):
    if b == 0:
        raise ZeroDivisionError("Modulo by zero")
    # Mimic PHP's modulo: sign follows dividend, truncating division toward zero
    return a - int(a / b) * b

def power(base, exp):
    return pow(base, exp)

def percent_of(percent, value):
    return value * percent / 100

def average(numbers):
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

def is_even(n):
    return n % 2 == 0

def round_to(x, places):
    # Use Decimal for half‑up rounding like PHP's round
    quant = Decimal('1e-{}'.format(places)) if places >= 0 else Decimal('1e{}'.format(-places))
    return float(Decimal(str(x)).quantize(quant, rounding=ROUND_HALF_UP))

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def factorial(n):
    if n < 0:
        raise ValueError("Negative input")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
