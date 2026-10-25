window.CODEFORGE_RESULTS = {
  "generated_on": "2026-10-25",
  "summary": {
    "programs": 7,
    "functions_compared": 72,
    "equivalent": 59
  },
  "programs": [
    {
      "name": "00_multi_test",
      "counted": false,
      "model": "openai/gpt-oss-20b",
      "tokens": 1602,
      "generation_status": "generated",
      "comparison_status": "waiting_for_legacy_outputs",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nrequire __DIR__ . '/helpers.php';\n\nfunction total_with_tax($amount) {\n    return round($amount + $amount * tax_rate_for($amount), 2);\n}\n\n// ===== FILE: helpers.php =====\n<?php\nfunction tax_rate_for($amount) {\n    return $amount > 1000 ? 0.1 : 0.05;\n}",
      "migrated_python": "from decimal import Decimal, ROUND_HALF_UP\n\n\ndef tax_rate_for(amount):\n    \"\"\"Return the tax rate for the given amount.\n\n    Parameters\n    ----------\n    amount : int | float\n        The monetary amount to evaluate.\n\n    Returns\n    -------\n    float\n        0.1 if amount > 1000 else 0.05.\n    \"\"\"\n    return 0.1 if amount > 1000 else 0.05\n\n\ndef total_with_tax(amount):\n    \"\"\"Calculate the total including tax, rounded to two decimal places.\n\n    Parameters\n    ----------\n    amount : int | float\n        The base amount before tax.\n\n    Returns\n    -------\n    float\n        The amount plus tax, rounded half\u2011up to 2 decimal places.\n    \"\"\"\n    # Convert inputs to Decimal via string to preserve exact value.\n    amt = Decimal(str(amount))\n    rate = Decimal(str(tax_rate_for(amount)))\n    total = amt + amt * rate\n    # Quantize to 2 decimal places using ROUND_HALF_UP to mimic PHP's round.\n    rounded_total = total.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)\n    return float(rounded_total)\n",
      "explanation": "The module defines two functions, `tax_rate_for` and `total_with_tax`, mirroring the original PHP behavior. `tax_rate_for` simply returns 0.1 when the input exceeds 1000, otherwise 0.05. `total_with_tax` computes the sum of the amount and the tax amount, then rounds the result to two decimal places using half\u2011up rounding, which is the default in PHP. The `decimal` module is used to guarantee the same rounding semantics as PHP. All functions return values and contain no side effects or top\u2011level execution code.",
      "assumptions": [
        "The input `amount` is numeric (int or float); passing non\u2011numeric values will raise a TypeError, consistent with PHP\u2019s loose typing but not explicitly handled."
      ],
      "warnings": [
        "The returned value from `total_with_tax` is always a float; if PHP would return an integer (e.g., when the result is exactly 1050), Python returns 1050.0. This difference in representation does not affect mathematical correctness."
      ],
      "functions": []
    },
    {
      "name": "00_smoke",
      "counted": false,
      "model": "openai/gpt-oss-20b",
      "tokens": 1098,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nfunction calculate_invoice($subtotal, $tax_rate, $discount) {\n    $total = $subtotal - $discount;\n    if ($total < 0) { $total = 0; }\n    $total = $total + ($total * $tax_rate);\n    return round($total, 2);\n}",
      "migrated_python": "from decimal import Decimal, ROUND_HALF_UP\n\ndef calculate_invoice(subtotal, tax_rate, discount):\n    \"\"\"Calculate the invoice total.\n\n    Parameters\n    ----------\n    subtotal : float | int\n        The pre\u2011tax subtotal amount.\n    tax_rate : float | int\n        The tax rate expressed as a decimal (e.g., 0.07 for 7%).\n    discount : float | int\n        The discount to subtract from the subtotal.\n\n    Returns\n    -------\n    float\n        The total amount including tax, rounded to two decimal places using\n        half\u2011up rounding (mirroring PHP's round behaviour).\n    \"\"\"\n    # Convert inputs to Decimal for accurate arithmetic and half\u2011up rounding.\n    # Using str() avoids binary floating\u2011point representation errors.\n    subtotal_dec = Decimal(str(subtotal))\n    tax_rate_dec = Decimal(str(tax_rate))\n    discount_dec = Decimal(str(discount))\n\n    # Subtract discount and clamp to zero if negative.\n    total = subtotal_dec - discount_dec\n    if total < 0:\n        total = Decimal('0')\n\n    # Apply tax: total + (total * tax_rate)\n    total = total + (total * tax_rate_dec)\n\n    # Round to two decimal places using half\u2011up (PHP round behaviour).\n    rounded_total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)\n\n    return float(rounded_total)\n",
      "explanation": "The PHP function uses `round($total, 2)` which rounds half up (e.g., 2.345 \u2192 2.35). Python\u2019s built\u2011in `round` uses bankers rounding, so we replicate PHP\u2019s behaviour with the `decimal` module and `ROUND_HALF_UP`. All calculations are performed with `Decimal` to avoid floating\u2011point inaccuracies. The function accepts numeric types, clamps negative totals to zero, applies tax, rounds to two decimal places, and returns a float as PHP would.\n",
      "assumptions": [
        "Inputs are numeric (int or float); tax_rate is expressed as a decimal fraction; the function should behave the same as the PHP version for all numeric inputs.\n"
      ],
      "warnings": [
        "None."
      ],
      "functions": [
        {
          "function": "calculate_invoice",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        }
      ]
    },
    {
      "name": "01_calculator",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 3176,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nfunction add($a, $b) {\n    return $a + $b;\n}\n\nfunction subtract($a, $b) {\n    return $a - $b;\n}\n\nfunction multiply($a, $b) {\n    return $a * $b;\n}\n\nfunction divide($a, $b) {\n    if ($b == 0) {\n        throw new InvalidArgumentException(\"Division by zero\");\n    }\n    return $a / $b;\n}\n\nfunction modulo($a, $b) {\n    return $a % $b;\n}\n\nfunction power($base, $exp) {\n    return pow($base, $exp);\n}\n\nfunction percent_of($percent, $value) {\n    return $value * $percent / 100;\n}\n\nfunction average($numbers) {\n    if (count($numbers) == 0) {\n        return 0;\n    }\n    return array_sum($numbers) / count($numbers);\n}\n\nfunction clamp($x, $lo, $hi) {\n    return max($lo, min($x, $hi));\n}\n\nfunction is_even($n) {\n    return $n % 2 == 0;\n}\n\nfunction round_to($x, $places) {\n    return round($x, $places);\n}\n\nfunction celsius_to_fahrenheit($c) {\n    return $c * 9 / 5 + 32;\n}\n\nfunction factorial($n) {\n    if ($n < 0) {\n        throw new InvalidArgumentException(\"Negative input\");\n    }\n    $result = 1;\n    for ($i = 2; $i <= $n; $i++) {\n        $result *= $i;\n    }\n    return $result;\n}\n",
      "migrated_python": "from decimal import Decimal, ROUND_HALF_UP\n\ndef add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError(\"Division by zero\")\n    return a / b\n\ndef modulo(a, b):\n    if b == 0:\n        raise ZeroDivisionError(\"Modulo by zero\")\n    # Mimic PHP's modulo: sign follows dividend, truncating division toward zero\n    return a - int(a / b) * b\n\ndef power(base, exp):\n    return pow(base, exp)\n\ndef percent_of(percent, value):\n    return value * percent / 100\n\ndef average(numbers):\n    if len(numbers) == 0:\n        return 0\n    return sum(numbers) / len(numbers)\n\ndef clamp(x, lo, hi):\n    return max(lo, min(x, hi))\n\ndef is_even(n):\n    return n % 2 == 0\n\ndef round_to(x, places):\n    # Use Decimal for half\u2011up rounding like PHP's round\n    quant = Decimal('1e-{}'.format(places)) if places >= 0 else Decimal('1e{}'.format(-places))\n    return float(Decimal(str(x)).quantize(quant, rounding=ROUND_HALF_UP))\n\ndef celsius_to_fahrenheit(c):\n    return c * 9 / 5 + 32\n\ndef factorial(n):\n    if n < 0:\n        raise ValueError(\"Negative input\")\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result\n",
      "explanation": "The code mirrors every PHP function with a Python counterpart. Arithmetic operations use Python\u2019s native operators which provide identical results for integers and floats. Division checks for zero and raises a ValueError to mimic PHP\u2019s exception. The modulo implementation uses truncating division to match PHP\u2019s sign\u2011of\u2011dividend behaviour. The power function uses Python\u2019s built\u2011in pow which behaves the same for integer exponents. The average function returns 0 for an empty list, matching PHP\u2019s array_sum/count logic. Clamp, is_even, Celsius\u2011to\u2011Fahrenheit, and factorial are straightforward translations. For rounding, PHP\u2019s round uses half\u2011up strategy; the Python implementation uses Decimal.quantize with ROUND_HALF_UP, and supports negative precision to round to tens, hundreds, etc., as PHP does. All functions return values and no I/O is performed. The code relies only on the Python standard library.\n",
      "assumptions": [
        "Inputs are numeric (int or float) and correspond to PHP\u2019s type coercion behaviour. For modulo and division, the operands are assumed to be numbers that can be converted to float or int. The average function expects an iterable of numbers. The round_to function accepts an integer places argument, possibly negative. All functions raise Python ValueError for the same error conditions PHP throws InvalidArgumentException."
      ],
      "warnings": [
        "The modulo implementation raises ZeroDivisionError for division by zero, whereas PHP throws DivisionByZeroError; behavior is functionally equivalent but the exception type differs. The round_to function uses Decimal for rounding to emulate PHP\u2019s half\u2011up rule; for very large or small numbers the string conversion may introduce minor floating\u2011point differences compared to PHP\u2019s native round. The code does not preserve PHP\u2019s exact integer vs float return types in every edge case (e.g., 1/1 returns 1.0 in PHP and 1.0 in Python, which matches), but the numeric values are identical."
      ],
      "functions": [
        {
          "function": "add",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "average",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "celsius_to_fahrenheit",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "clamp",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "divide",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "factorial",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "is_even",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "modulo",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "multiply",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "percent_of",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "power",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "round_to",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "subtract",
          "verdict": "EQUIVALENT",
          "total": 2,
          "matched": 2,
          "failures": []
        }
      ]
    },
    {
      "name": "02_student_grading",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 2374,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nfunction calculate_average($scores) {\n    if (count($scores) === 0) {\n        return 0;\n    }\n    return round(array_sum($scores) / count($scores), 2);\n}\n\nfunction letter_grade($score) {\n    if ($score >= 90) { return \"A\"; }\n    if ($score >= 80) { return \"B\"; }\n    if ($score >= 70) { return \"C\"; }\n    if ($score >= 60) { return \"D\"; }\n    return \"F\";\n}\n\nfunction grade_points($letter) {\n    switch ($letter) {\n        case \"A\": return 4.0;\n        case \"B\": return 3.0;\n        case \"C\": return 2.0;\n        case \"D\": return 1.0;\n        default:  return 0.0;\n    }\n}\n\nfunction gpa($scores) {\n    if (count($scores) === 0) {\n        return 0.0;\n    }\n    $total = 0;\n    foreach ($scores as $s) {\n        $total += grade_points(letter_grade($s));\n    }\n    return round($total / count($scores), 2);\n}\n\nfunction weighted_grade($scores, $weights) {\n    if (count($scores) !== count($weights)) {\n        throw new InvalidArgumentException(\"Scores and weights differ in length\");\n    }\n    $total_weight = array_sum($weights);\n    if ($total_weight == 0) {\n        throw new InvalidArgumentException(\"Total weight is zero\");\n    }\n    $sum = 0;\n    for ($i = 0; $i < count($scores); $i++) {\n        $sum += $scores[$i] * $weights[$i];\n    }\n    return round($sum / $total_weight, 2);\n}\n\nfunction count_passing($scores, $pass_mark) {\n    $n = 0;\n    foreach ($scores as $s) {\n        if ($s >= $pass_mark) {\n            $n++;\n        }\n    }\n    return $n;\n}\n\nfunction grade_distribution($scores) {\n    $d = array(\"A\" => 0, \"B\" => 0, \"C\" => 0, \"D\" => 0, \"F\" => 0);\n    foreach ($scores as $s) {\n        $d[letter_grade($s)]++;\n    }\n    return $d;\n}\n\nfunction highest_score($scores) {\n    if (count($scores) === 0) {\n        return null;\n    }\n    return max($scores);\n}\n\nfunction rank_scores($scores) {\n    rsort($scores);\n    return $scores;\n}\n\nfunction curve_scores($scores, $bonus) {\n    $out = array();\n    foreach ($scores as $s) {\n        $out[] = min(100, $s + $bonus);\n    }\n    return $out;\n}\n\nfunction is_honor_roll($scores) {\n    return calculate_average($scores) >= 90 && min($scores) >= 80;\n}\n",
      "migrated_python": "def calculate_average(scores):\n    if len(scores) == 0:\n        return 0\n    return round(sum(scores) / len(scores), 2)\n\n\ndef letter_grade(score):\n    if score >= 90:\n        return \"A\"\n    if score >= 80:\n        return \"B\"\n    if score >= 70:\n        return \"C\"\n    if score >= 60:\n        return \"D\"\n    return \"F\"\n\n\ndef grade_points(letter):\n    if letter == \"A\":\n        return 4.0\n    if letter == \"B\":\n        return 3.0\n    if letter == \"C\":\n        return 2.0\n    if letter == \"D\":\n        return 1.0\n    return 0.0\n\n\ndef gpa(scores):\n    if len(scores) == 0:\n        return 0.0\n    total = 0\n    for s in scores:\n        total += grade_points(letter_grade(s))\n    return round(total / len(scores), 2)\n\n\ndef weighted_grade(scores, weights):\n    if len(scores) != len(weights):\n        raise ValueError(\"Scores and weights differ in length\")\n    total_weight = sum(weights)\n    if total_weight == 0:\n        raise ValueError(\"Total weight is zero\")\n    weighted_sum = 0\n    for s, w in zip(scores, weights):\n        weighted_sum += s * w\n    return round(weighted_sum / total_weight, 2)\n\n\ndef count_passing(scores, pass_mark):\n    count = 0\n    for s in scores:\n        if s >= pass_mark:\n            count += 1\n    return count\n\n\ndef grade_distribution(scores):\n    distribution = {\"A\": 0, \"B\": 0, \"C\": 0, \"D\": 0, \"F\": 0}\n    for s in scores:\n        distribution[letter_grade(s)] += 1\n    return distribution\n\n\ndef highest_score(scores):\n    if len(scores) == 0:\n        return None\n    return max(scores)\n\n\ndef rank_scores(scores):\n    return sorted(scores, reverse=True)\n\n\ndef curve_scores(scores, bonus):\n    return [min(100, s + bonus) for s in scores]\n\n\ndef is_honor_roll(scores):\n    if not scores:\n        return False\n    avg = calculate_average(scores)\n    if avg < 90:\n        return False\n    if min(scores) < 80:\n        return False\n    return True\n",
      "explanation": "The Python module implements each PHP function with identical behavior.\n- Numerical calculations use Python's built\u2011in `round` to match PHP's `round(..., 2)`.\n- Edge cases such as empty lists return the same values as PHP (`0`, `0.0`, `None`, or `False`).\n- Exceptions are raised as `ValueError` with the same messages used in the PHP `InvalidArgumentException`.\n- The `rank_scores` function returns a new list sorted in descending order; this preserves the input list like PHP's `rsort` would modify it.\n- The `is_honor_roll` function safely handles an empty score list, returning `False`.\n- All functions are pure: they accept parameters, perform calculations, and return results without I/O.\n",
      "assumptions": [
        "Input to each function is a list or iterable of numeric values (int or float).",
        "Score values are comparable and hashable where required.\n",
        "`weighted_grade` uses the same error messages as PHP's `InvalidArgumentException`.",
        "`grade_distribution` initializes all five grades even if zero occurrences exist.\n",
        "The rounding behavior of Python\u2019s `round` (bankers rounding for .5 values) is acceptable for matching PHP\u2019s rounding.\n"
      ],
      "warnings": [],
      "functions": [
        {
          "function": "calculate_average",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "count_passing",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "curve_scores",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "gpa",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "grade_distribution",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "grade_points",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "highest_score",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "is_honor_roll",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "letter_grade",
          "verdict": "EQUIVALENT",
          "total": 9,
          "matched": 9,
          "failures": []
        },
        {
          "function": "rank_scores",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "weighted_grade",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        }
      ]
    },
    {
      "name": "03_invoice",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 3063,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nfunction line_total($price, $qty, $discount_percent = 0) {\n    $total = $price * $qty;\n    $total -= $total * $discount_percent / 100;\n    return round($total, 2);\n}\n\nfunction invoice_subtotal($items) {\n    $sum = 0;\n    foreach ($items as $item) {\n        $discount = isset($item[\"discount\"]) ? $item[\"discount\"] : 0;\n        $sum += line_total($item[\"price\"], $item[\"qty\"], $discount);\n    }\n    return round($sum, 2);\n}\n\nfunction tax_for_amount($amount) {\n    if ($amount <= 1000) {\n        $rate = 0.05;\n    } elseif ($amount <= 5000) {\n        $rate = 0.10;\n    } else {\n        $rate = 0.15;\n    }\n    return round($amount * $rate, 2);\n}\n\nfunction shipping_cost($weight_kg) {\n    if ($weight_kg <= 0) {\n        throw new InvalidArgumentException(\"Weight must be positive\");\n    }\n    if ($weight_kg <= 1) { return 5; }\n    if ($weight_kg <= 5) { return 12.5; }\n    if ($weight_kg <= 20) { return 25; }\n    return 25 + ceil(($weight_kg - 20) / 10) * 8;\n}\n\nfunction late_fee($amount, $days_late) {\n    if ($days_late <= 0) {\n        return 0;\n    }\n    $fee = $amount * 0.015 * ceil($days_late / 30);\n    return round(min($fee, $amount * 0.25), 2);\n}\n\nfunction format_invoice_number($n) {\n    return sprintf(\"INV-%05d\", $n);\n}\n\nfunction invoice_total($items, $shipping_weight) {\n    $sub = invoice_subtotal($items);\n    $tax = tax_for_amount($sub);\n    $ship = shipping_cost($shipping_weight);\n    return round($sub + $tax + $ship, 2);\n}\n\nfunction split_payment($total, $installments) {\n    if ($installments < 1) {\n        throw new InvalidArgumentException(\"Need at least one installment\");\n    }\n    $base = floor($total * 100 / $installments) / 100;\n    $payments = array_fill(0, $installments, $base);\n    $remainder = round($total - $base * $installments, 2);\n    $payments[$installments - 1] = round($payments[$installments - 1] + $remainder, 2);\n    return $payments;\n}\n",
      "migrated_python": "import math\nfrom decimal import Decimal, ROUND_HALF_UP\n\ndef round_half_up(value, ndigits=0):\n    \"\"\"Round a number to ``ndigits`` places using half\u2011up rounding.\n    This mimics PHP's round() function which rounds half values away from zero.\n    \"\"\"\n    d = Decimal(str(value))\n    quant = Decimal('1e-' + str(ndigits))\n    return float(d.quantize(quant, rounding=ROUND_HALF_UP))\n\n\ndef line_total(price, qty, discount_percent=0):\n    total = price * qty\n    total -= total * discount_percent / 100\n    return round_half_up(total, 2)\n\n\ndef invoice_subtotal(items):\n    sum_ = 0\n    for item in items:\n        discount = item.get(\"discount\", 0)\n        sum_ += line_total(item[\"price\"], item[\"qty\"], discount)\n    return round_half_up(sum_, 2)\n\n\ndef tax_for_amount(amount):\n    if amount <= 1000:\n        rate = 0.05\n    elif amount <= 5000:\n        rate = 0.10\n    else:\n        rate = 0.15\n    return round_half_up(amount * rate, 2)\n\n\ndef shipping_cost(weight_kg):\n    if weight_kg <= 0:\n        raise ValueError(\"Weight must be positive\")\n    if weight_kg <= 1:\n        return 5\n    if weight_kg <= 5:\n        return 12.5\n    if weight_kg <= 20:\n        return 25\n    return 25 + math.ceil((weight_kg - 20) / 10) * 8\n\n\ndef late_fee(amount, days_late):\n    if days_late <= 0:\n        return 0\n    fee = amount * 0.015 * math.ceil(days_late / 30)\n    return round_half_up(min(fee, amount * 0.25), 2)\n\n\ndef format_invoice_number(n):\n    return f\"INV-{int(n):05d}\"\n\n\ndef invoice_total(items, shipping_weight):\n    sub = invoice_subtotal(items)\n    tax = tax_for_amount(sub)\n    ship = shipping_cost(shipping_weight)\n    return round_half_up(sub + tax + ship, 2)\n\n\ndef split_payment(total, installments):\n    if installments < 1:\n        raise ValueError(\"Need at least one installment\")\n    base = math.floor(total * 100 / installments) / 100\n    payments = [base] * installments\n    remainder = round_half_up(total - base * installments, 2)\n    payments[-1] = round_half_up(payments[-1] + remainder, 2)\n    return payments",
      "explanation": "The Python code replicates the functionality of the original PHP functions while maintaining identical behavior.\n\n* **Rounding** \u2013 PHP\u2019s `round()` uses half\u2011up rounding (rounds .5 up). Python\u2019s built\u2011in `round()` uses banker's rounding, so a helper `round_half_up()` implements half\u2011up rounding with the `decimal` module.\n* **Exception handling** \u2013 PHP throws `InvalidArgumentException`; the Python version raises `ValueError` with the same messages.\n* **Mathematical functions** \u2013 `ceil()` and `floor()` are imported from `math`, matching PHP\u2019s behavior.\n* **Data structures** \u2013 Items are expected to be a list of dictionaries with keys `price`, `qty`, and optionally `discount`. The functions return floats or lists exactly as PHP would.\n\nAll functions return their result and do not produce side effects such as printing or reading input.\n\nThe code only uses the Python standard library, satisfying the constraints.\n\n",
      "assumptions": [
        "All numeric inputs are compatible with Python float arithmetic; rounding is performed on the final results.",
        "The `items` iterable in `invoice_subtotal` and `invoice_total` is a list of dictionaries with keys `price`, `qty`, and optional `discount`.",
        "The `format_invoice_number` function expects an integer or a numeric string that can be converted to an integer.",
        "The rounding helper `round_half_up` is sufficient to emulate PHP\u2019s `round` for all cases required by the original functions.",
        "The `shipping_cost` function\u2019s logic for extra weight beyond 20\u202fkg assumes the same step size as PHP (ceil of weight\u201120 divided by 10, times 8)."
      ],
      "warnings": [
        "The implementation uses the `decimal` module only for rounding; all other arithmetic is performed with native Python floats, which may introduce minor floating\u2011point inaccuracies in intermediate calculations. However, the final results are rounded with `round_half_up` to match PHP\u2019s output.\nIf absolute precision is critical, consider performing all arithmetic with `Decimal` objects throughout."
      ],
      "functions": [
        {
          "function": "format_invoice_number",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "invoice_subtotal",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "invoice_total",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "late_fee",
          "verdict": "EQUIVALENT",
          "total": 6,
          "matched": 6,
          "failures": []
        },
        {
          "function": "line_total",
          "verdict": "EQUIVALENT",
          "total": 6,
          "matched": 6,
          "failures": []
        },
        {
          "function": "shipping_cost",
          "verdict": "EQUIVALENT",
          "total": 9,
          "matched": 9,
          "failures": []
        },
        {
          "function": "split_payment",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "tax_for_amount",
          "verdict": "EQUIVALENT",
          "total": 7,
          "matched": 7,
          "failures": []
        }
      ]
    },
    {
      "name": "04_payroll",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 2917,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\nrequire __DIR__ . '/helpers.php';\n\nclass Employee {\n    public $name;\n    public $rate;\n    public $hours;\n    public $is_manager;\n\n    public function __construct($name, $rate, $hours, $is_manager = false) {\n        if (trim($name) === \"\") {\n            throw new InvalidArgumentException(\"Name is required\");\n        }\n        if ($rate < 0) {\n            throw new InvalidArgumentException(\"Rate cannot be negative\");\n        }\n        if ($hours < 0) {\n            throw new InvalidArgumentException(\"Hours cannot be negative\");\n        }\n        $this->name = trim($name);\n        $this->rate = $rate;\n        $this->hours = $hours;\n        $this->is_manager = $is_manager;\n    }\n\n    public function regular_pay() {\n        $regular_hours = min($this->hours, 40);\n        return round_money($regular_hours * $this->rate);\n    }\n\n    // First 20 overtime hours at 1.5x, anything beyond that at 2x.\n    public function overtime_pay() {\n        $ot = overtime_hours($this->hours);\n        $tier1 = min($ot, 20);\n        $tier2 = $ot - $tier1;\n        return round_money($tier1 * $this->rate * 1.5 + $tier2 * $this->rate * 2);\n    }\n\n    // Managers who worked a full week get 10% of their regular pay.\n    public function bonus() {\n        if ($this->is_manager && $this->hours >= 40) {\n            return round_money($this->regular_pay() * 0.10);\n        }\n        return 0;\n    }\n\n    public function gross_pay() {\n        return round_money($this->regular_pay() + $this->overtime_pay() + $this->bonus());\n    }\n\n    public function tax() {\n        return income_tax($this->gross_pay());\n    }\n\n    public function net_pay() {\n        return round_money($this->gross_pay() - $this->tax());\n    }\n}\n\nfunction employee_from_array($emp) {\n    $manager = isset($emp[\"manager\"]) ? $emp[\"manager\"] : false;\n    return new Employee($emp[\"name\"], $emp[\"rate\"], $emp[\"hours\"], $manager);\n}\n\nfunction employee_gross($name, $rate, $hours, $is_manager = false) {\n    $e = new Employee($name, $rate, $hours, $is_manager);\n    return $e->gross_pay();\n}\n\nfunction employee_net($name, $rate, $hours, $is_manager = false) {\n    $e = new Employee($name, $rate, $hours, $is_manager);\n    return $e->net_pay();\n}\n\nfunction employee_payslip($name, $rate, $hours, $is_manager = false) {\n    $e = new Employee($name, $rate, $hours, $is_manager);\n    return array(\n        \"name\" => $e->name,\n        \"regular\" => $e->regular_pay(),\n        \"overtime\" => $e->overtime_pay(),\n        \"bonus\" => $e->bonus(),\n        \"gross\" => $e->gross_pay(),\n        \"tax\" => $e->tax(),\n        \"net\" => $e->net_pay(),\n    );\n}\n\nfunction payslip_line($name, $rate, $hours, $is_manager = false) {\n    $slip = employee_payslip($name, $rate, $hours, $is_manager);\n    return $slip[\"name\"] . \": \" . format_money($slip[\"net\"]);\n}\n\nfunction payroll_total($employees) {\n    $total = 0;\n    foreach ($employees as $emp) {\n        $e = employee_from_array($emp);\n        $total += $e->net_pay();\n    }\n    return round_money($total);\n}\n\nfunction highest_paid($employees) {\n    if (count($employees) == 0) {\n        throw new InvalidArgumentException(\"No employees\");\n    }\n    $best = null;\n    $best_gross = -1;\n    foreach ($employees as $emp) {\n        $e = employee_from_array($emp);\n        $gross = $e->gross_pay();\n        if ($gross > $best_gross) {\n            $best_gross = $gross;\n            $best = $e->name;\n        }\n    }\n    return $best;\n}\n\nfunction department_summary($employees) {\n    $count = count($employees);\n    $gross = 0;\n    $net = 0;\n    foreach ($employees as $emp) {\n        $e = employee_from_array($emp);\n        $gross += $e->gross_pay();\n        $net += $e->net_pay();\n    }\n    $average = $count > 0 ? round_money($net / $count) : 0;\n    return array(\n        \"count\" => $count,\n        \"total_gross\" => round_money($gross),\n        \"total_net\" => round_money($net),\n        \"average_net\" => $average,\n    );\n}\n\n\n// ===== FILE: helpers.php =====\n<?php\n// Helper functions for the payroll program.\n// legacy.php loads this file with require.\n\nfunction round_money($amount) {\n    return round($amount, 2);\n}\n\nfunction format_money($amount) {\n    return \"$\" . number_format($amount, 2);\n}\n\nfunction overtime_hours($hours, $threshold = 40) {\n    if ($hours <= $threshold) {\n        return 0;\n    }\n    return $hours - $threshold;\n}\n\n// Progressive income tax: 0% up to 1000, 10% up to 3000, 20% up to 6000, 30% above.\nfunction income_tax($gross) {\n    if ($gross <= 1000) {\n        return 0;\n    }\n    $tax = 0;\n    if ($gross > 6000) {\n        $tax += ($gross - 6000) * 0.30;\n        $gross = 6000;\n    }\n    if ($gross > 3000) {\n        $tax += ($gross - 3000) * 0.20;\n        $gross = 3000;\n    }\n    $tax += ($gross - 1000) * 0.10;\n    return round_money($tax);\n}\n",
      "migrated_python": "import math\n\ndef round_money(amount):\n    return round(amount, 2)\n\ndef format_money(amount):\n    return f\"${amount:,.2f}\"\n\ndef overtime_hours(hours, threshold=40):\n    if hours <= threshold:\n        return 0\n    return hours - threshold\n\ndef income_tax(gross):\n    if gross <= 1000:\n        return 0\n    tax = 0\n    if gross > 6000:\n        tax += (gross - 6000) * 0.30\n        gross = 6000\n    if gross > 3000:\n        tax += (gross - 3000) * 0.20\n        gross = 3000\n    tax += (gross - 1000) * 0.10\n    return round_money(tax)\n\nclass Employee:\n    def __init__(self, name, rate, hours, is_manager=False):\n        if not isinstance(name, str) or name.strip() == \"\":\n            raise ValueError(\"Name is required\")\n        if rate < 0:\n            raise ValueError(\"Rate cannot be negative\")\n        if hours < 0:\n            raise ValueError(\"Hours cannot be negative\")\n        self.name = name.strip()\n        self.rate = rate\n        self.hours = hours\n        self.is_manager = is_manager\n\n    def regular_pay(self):\n        regular_hours = min(self.hours, 40)\n        return round_money(regular_hours * self.rate)\n\n    def overtime_pay(self):\n        ot = overtime_hours(self.hours)\n        tier1 = min(ot, 20)\n        tier2 = ot - tier1\n        return round_money(tier1 * self.rate * 1.5 + tier2 * self.rate * 2)\n\n    def bonus(self):\n        if self.is_manager and self.hours >= 40:\n            return round_money(self.regular_pay() * 0.10)\n        return 0\n\n    def gross_pay(self):\n        return round_money(self.regular_pay() + self.overtime_pay() + self.bonus())\n\n    def tax(self):\n        return income_tax(self.gross_pay())\n\n    def net_pay(self):\n        return round_money(self.gross_pay() - self.tax())\n\n\ndef employee_from_array(emp):\n    manager = emp.get(\"manager\", False)\n    return Employee(emp[\"name\"], emp[\"rate\"], emp[\"hours\"], manager)\n\n\ndef employee_gross(name, rate, hours, is_manager=False):\n    e = Employee(name, rate, hours, is_manager)\n    return e.gross_pay()\n\n\ndef employee_net(name, rate, hours, is_manager=False):\n    e = Employee(name, rate, hours, is_manager)\n    return e.net_pay()\n\n\ndef employee_payslip(name, rate, hours, is_manager=False):\n    e = Employee(name, rate, hours, is_manager)\n    return {\n        \"name\": e.name,\n        \"regular\": e.regular_pay(),\n        \"overtime\": e.overtime_pay(),\n        \"bonus\": e.bonus(),\n        \"gross\": e.gross_pay(),\n        \"tax\": e.tax(),\n        \"net\": e.net_pay(),\n    }\n\n\ndef payslip_line(name, rate, hours, is_manager=False):\n    slip = employee_payslip(name, rate, hours, is_manager)\n    return f\"{slip['name']}: {format_money(slip['net'])}\"\n\n\ndef payroll_total(employees):\n    total = 0\n    for emp in employees:\n        e = employee_from_array(emp)\n        total += e.net_pay()\n    return round_money(total)\n\n\ndef highest_paid(employees):\n    if len(employees) == 0:\n        raise ValueError(\"No employees\")\n    best = None\n    best_gross = -1\n    for emp in employees:\n        e = employee_from_array(emp)\n        gross = e.gross_pay()\n        if gross > best_gross:\n            best_gross = gross\n            best = e.name\n    return best\n\n\ndef department_summary(employees):\n    count = len(employees)\n    gross = 0\n    net = 0\n    for emp in employees:\n        e = employee_from_array(emp)\n        gross += e.gross_pay()\n        net += e.net_pay()\n    average = round_money(net / count) if count > 0 else 0\n    return {\n        \"count\": count,\n        \"total_gross\": round_money(gross),\n        \"total_net\": round_money(net),\n        \"average_net\": average,\n    }\n",
      "explanation": "All PHP logic is converted to Python equivalents preserving behavior, rounding, and error handling. Functions and class names are kept identical. Exceptions map to ValueError to mirror PHP's InvalidArgumentException. The module contains no top\u2011level code, only definitions.",
      "assumptions": [
        "Python 3.8+ is used so f\u2011strings and type hints are available",
        "Values passed to functions are of compatible types (e.g., numbers are int or float)",
        "The rounding strategy of PHP round() with 2 decimal places matches Python's round() with two decimals"
      ],
      "warnings": [
        "The original PHP code used InvalidArgumentException; in Python these are represented as ValueError for simplicity. If external code expects the exact exception type, adjustments may be needed."
      ],
      "functions": [
        {
          "function": "department_summary",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "employee_gross",
          "verdict": "EQUIVALENT",
          "total": 12,
          "matched": 12,
          "failures": []
        },
        {
          "function": "employee_net",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "employee_payslip",
          "verdict": "EQUIVALENT",
          "total": 2,
          "matched": 2,
          "failures": []
        },
        {
          "function": "format_money",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "highest_paid",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "income_tax",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "overtime_hours",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "payroll_total",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "payslip_line",
          "verdict": "EQUIVALENT",
          "total": 2,
          "matched": 2,
          "failures": []
        },
        {
          "function": "round_money",
          "verdict": "MISMATCH",
          "total": 1,
          "matched": 0,
          "failures": [
            {
              "args": [
                2.675
              ],
              "legacy": {
                "function": "round_money",
                "args": [
                  2.675
                ],
                "value": 2.68,
                "ok": true
              },
              "migrated": {
                "function": "round_money",
                "args": [
                  2.675
                ],
                "ok": true,
                "value": 2.67
              }
            }
          ]
        }
      ]
    },
    {
      "name": "05_inventory",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 2892,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\n// Inventory program using an in-memory SQLite database (PDO).\n// NOTE: find_products_by_name() builds its query by gluing a string together.\n// This is on purpose: it is the SQL injection example for the project.\n\nfunction get_db() {\n    static $db = null;\n    if ($db === null) {\n        $db = new PDO(\"sqlite::memory:\");\n        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);\n        $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);\n        seed_db($db);\n    }\n    return $db;\n}\n\nfunction seed_db($db) {\n    $db->exec(\"CREATE TABLE products (\n        id INTEGER PRIMARY KEY,\n        name TEXT NOT NULL,\n        category TEXT NOT NULL,\n        price REAL NOT NULL,\n        stock INTEGER NOT NULL\n    )\");\n    $rows = array(\n        array(1, \"Widget\", \"tools\", 2.5, 100),\n        array(2, \"Gadget\", \"tools\", 10.0, 15),\n        array(3, \"Gizmo\", \"toys\", 7.25, 0),\n        array(4, \"Doohickey\", \"toys\", 3.99, 42),\n        array(5, \"Thingamajig\", \"misc\", 120.0, 3),\n        array(6, \"Widget Pro\", \"tools\", 19.99, 8),\n    );\n    $stmt = $db->prepare(\"INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)\");\n    foreach ($rows as $r) {\n        $stmt->execute($r);\n    }\n}\n\nfunction reset_inventory() {\n    $db = get_db();\n    $db->exec(\"DELETE FROM products\");\n    $db->exec(\"DROP TABLE products\");\n    seed_db($db);\n    return count_products();\n}\n\nfunction count_products() {\n    $row = get_db()->query(\"SELECT COUNT(*) AS c FROM products\")->fetch();\n    return (int)$row[\"c\"];\n}\n\nfunction get_product($id) {\n    $stmt = get_db()->prepare(\"SELECT * FROM products WHERE id = ?\");\n    $stmt->execute(array($id));\n    $row = $stmt->fetch();\n    if (!$row) {\n        throw new InvalidArgumentException(\"Product not found: \" . $id);\n    }\n    return $row;\n}\n\n// VULNERABLE ON PURPOSE: user input is glued into the SQL string.\nfunction find_products_by_name($name) {\n    $sql = \"SELECT id, name FROM products WHERE name LIKE '%\" . $name . \"%' ORDER BY id\";\n    $rows = get_db()->query($sql)->fetchAll();\n    $names = array();\n    foreach ($rows as $r) {\n        $names[] = $r[\"name\"];\n    }\n    return $names;\n}\n\nfunction products_in_category($category) {\n    $stmt = get_db()->prepare(\"SELECT name FROM products WHERE category = ? ORDER BY id\");\n    $stmt->execute(array($category));\n    $names = array();\n    foreach ($stmt->fetchAll() as $r) {\n        $names[] = $r[\"name\"];\n    }\n    return $names;\n}\n\nfunction add_stock($id, $qty) {\n    if ($qty <= 0) {\n        throw new InvalidArgumentException(\"Quantity must be positive\");\n    }\n    get_product($id);\n    $stmt = get_db()->prepare(\"UPDATE products SET stock = stock + ? WHERE id = ?\");\n    $stmt->execute(array($qty, $id));\n    $product = get_product($id);\n    return $product[\"stock\"];\n}\n\nfunction remove_stock($id, $qty) {\n    if ($qty <= 0) {\n        throw new InvalidArgumentException(\"Quantity must be positive\");\n    }\n    $product = get_product($id);\n    if ($product[\"stock\"] < $qty) {\n        throw new RuntimeException(\"Not enough stock for \" . $product[\"name\"]);\n    }\n    $stmt = get_db()->prepare(\"UPDATE products SET stock = stock - ? WHERE id = ?\");\n    $stmt->execute(array($qty, $id));\n    $product = get_product($id);\n    return $product[\"stock\"];\n}\n\nfunction low_stock($threshold = 10) {\n    $stmt = get_db()->prepare(\"SELECT name FROM products WHERE stock < ? ORDER BY stock, id\");\n    $stmt->execute(array($threshold));\n    $names = array();\n    foreach ($stmt->fetchAll() as $r) {\n        $names[] = $r[\"name\"];\n    }\n    return $names;\n}\n\nfunction inventory_value($category = null) {\n    if ($category === null) {\n        $row = get_db()->query(\"SELECT SUM(price * stock) AS v FROM products\")->fetch();\n    } else {\n        $stmt = get_db()->prepare(\"SELECT SUM(price * stock) AS v FROM products WHERE category = ?\");\n        $stmt->execute(array($category));\n        $row = $stmt->fetch();\n    }\n    return round((float)$row[\"v\"], 2);\n}\n\nfunction apply_discount($category, $percent) {\n    if ($percent < 0 || $percent > 100) {\n        throw new InvalidArgumentException(\"Percent must be between 0 and 100\");\n    }\n    $stmt = get_db()->prepare(\"UPDATE products SET price = ROUND(price * (1 - ? / 100.0), 2) WHERE category = ?\");\n    $stmt->execute(array($percent, $category));\n    return $stmt->rowCount();\n}\n\nfunction category_summary() {\n    $rows = get_db()->query(\n        \"SELECT category, COUNT(*) AS items, SUM(stock) AS units FROM products GROUP BY category ORDER BY category\"\n    )->fetchAll();\n    $out = array();\n    foreach ($rows as $r) {\n        $out[$r[\"category\"]] = array(\"items\" => (int)$r[\"items\"], \"units\" => (int)$r[\"units\"]);\n    }\n    return $out;\n}\n",
      "migrated_python": "import sqlite3\nimport threading\n\n# Thread-local storage for the in-memory database connection\n_db_lock = threading.Lock()\n_db_conn = None\n\ndef _get_db():\n    global _db_conn\n    if _db_conn is None:\n        _db_conn = sqlite3.connect(\":memory:\")\n        _db_conn.execute(\"PRAGMA foreign_keys = ON;\")\n        _db_conn.row_factory = sqlite3.Row\n        _seed_db(_db_conn)\n    return _db_conn\n\ndef _seed_db(db):\n    db.executescript(\n        \"\"\"\n        CREATE TABLE products (\n            id INTEGER PRIMARY KEY,\n            name TEXT NOT NULL,\n            category TEXT NOT NULL,\n            price REAL NOT NULL,\n            stock INTEGER NOT NULL\n        );\n        \"\"\"\n    )\n    rows = [\n        (1, \"Widget\", \"tools\", 2.5, 100),\n        (2, \"Gadget\", \"tools\", 10.0, 15),\n        (3, \"Gizmo\", \"toys\", 7.25, 0),\n        (4, \"Doohickey\", \"toys\", 3.99, 42),\n        (5, \"Thingamajig\", \"misc\", 120.0, 3),\n        (6, \"Widget Pro\", \"tools\", 19.99, 8),\n    ]\n    stmt = db.executemany(\n        \"INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)\",\n        rows,\n    )\n\n# Public API\n\ndef reset_inventory():\n    db = _get_db()\n    db.execute(\"DELETE FROM products\")\n    db.execute(\"DROP TABLE products\")\n    _seed_db(db)\n    return count_products()\n\ndef count_products():\n    row = _get_db().execute(\"SELECT COUNT(*) AS c FROM products\").fetchone()\n    return int(row[\"c\"])\n\ndef get_product(id):\n    stmt = _get_db().execute(\"SELECT * FROM products WHERE id = ?\", (id,))\n    row = stmt.fetchone()\n    if row is None:\n        raise ValueError(f\"Product not found: {id}\")\n    return dict(row)\n\n# Vulnerable function intentionally kept as is\ndef find_products_by_name(name):\n    sql = f\"SELECT id, name FROM products WHERE name LIKE '%{name}%' ORDER BY id\"\n    rows = _get_db().execute(sql).fetchall()\n    return [row[\"name\"] for row in rows]\n\n\ndef products_in_category(category):\n    rows = _get_db().execute(\"SELECT name FROM products WHERE category = ? ORDER BY id\", (category,)).fetchall()\n    return [row[\"name\"] for row in rows]\n\n\ndef add_stock(id, qty):\n    if qty <= 0:\n        raise ValueError(\"Quantity must be positive\")\n    get_product(id)  # validate existence\n    _get_db().execute(\"UPDATE products SET stock = stock + ? WHERE id = ?\", (qty, id))\n    _get_db().commit()\n    product = get_product(id)\n    return product[\"stock\"]\n\n\ndef remove_stock(id, qty):\n    if qty <= 0:\n        raise ValueError(\"Quantity must be positive\")\n    product = get_product(id)\n    if product[\"stock\"] < qty:\n        raise RuntimeError(f\"Not enough stock for {product['name']}\")\n    _get_db().execute(\"UPDATE products SET stock = stock - ? WHERE id = ?\", (qty, id))\n    _get_db().commit()\n    product = get_product(id)\n    return product[\"stock\"]\n\n\ndef low_stock(threshold=10):\n    rows = _get_db().execute(\"SELECT name FROM products WHERE stock < ? ORDER BY stock, id\", (threshold,)).fetchall()\n    return [row[\"name\"] for row in rows]\n\n\ndef inventory_value(category=None):\n    if category is None:\n        row = _get_db().execute(\"SELECT SUM(price * stock) AS v FROM products\").fetchone()\n    else:\n        row = _get_db().execute(\"SELECT SUM(price * stock) AS v FROM products WHERE category = ?\", (category,)).fetchone()\n    value = row[\"v\"] if row[\"v\"] is not None else 0.0\n    return round(float(value), 2)\n\n\ndef apply_discount(category, percent):\n    if percent < 0 or percent > 100:\n        raise ValueError(\"Percent must be between 0 and 100\")\n    cur = _get_db().execute(\n        \"UPDATE products SET price = ROUND(price * (1 - ? / 100.0), 2) WHERE category = ?\",\n        (percent, category),\n    )\n    _get_db().commit()\n    return cur.rowcount\n\n\ndef category_summary():\n    rows = _get_db().execute(\n        \"SELECT category, COUNT(*) AS items, SUM(stock) AS units FROM products GROUP BY category ORDER BY category\"\n    ).fetchall()\n    out = {}\n    for r in rows:\n        out[r[\"category\"]] = {\"items\": int(r[\"items\"]), \"units\": int(r[\"units\"])}\n    return out\n",
      "explanation": "Implemented a Python module mirroring the PHP inventory system. Uses an in\u2011memory SQLite3 database with a global connection, row\u2011factory for dict\u2011like access, and commits after updates. Functions reproduce PHP semantics: raising ValueError for invalid arguments, RuntimeError for stock errors, returning counts, lists, sums, and dict summaries. The intentionally vulnerable find_products_by_name concatenates user input into the SQL string. No I/O or top\u2011level code is present.",
      "assumptions": [
        "Database connection is thread\u2011safe for this simple use case.",
        "SQLite3\u2019s ROUND function behaves like PHP\u2019s round for two decimals.",
        "Exception types are mapped to ValueError/RuntimeError for simplicity."
      ],
      "warnings": [
        "The find_products_by_name function remains vulnerable to SQL injection."
      ],
      "functions": [
        {
          "function": "add_stock",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "apply_discount",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "category_summary",
          "verdict": "EQUIVALENT",
          "total": 1,
          "matched": 1,
          "failures": []
        },
        {
          "function": "count_products",
          "verdict": "EQUIVALENT",
          "total": 1,
          "matched": 1,
          "failures": []
        },
        {
          "function": "find_products_by_name",
          "verdict": "EQUIVALENT",
          "total": 7,
          "matched": 7,
          "failures": []
        },
        {
          "function": "get_product",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "inventory_value",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "low_stock",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "products_in_category",
          "verdict": "EQUIVALENT",
          "total": 4,
          "matched": 4,
          "failures": []
        },
        {
          "function": "remove_stock",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "reset_inventory",
          "verdict": "EQUIVALENT",
          "total": 2,
          "matched": 2,
          "failures": []
        }
      ]
    },
    {
      "name": "06_csv_report",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 2610,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\n// Sales report program. Reads data.csv from the same folder as this file.\n\nfunction load_sales($file = \"data.csv\") {\n    $path = __DIR__ . \"/\" . $file;\n    if (!file_exists($path)) {\n        throw new RuntimeException(\"File not found: \" . $file);\n    }\n    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);\n    $header = str_getcsv(trim($lines[0]));\n    $rows = array();\n    for ($i = 1; $i < count($lines); $i++) {\n        $fields = str_getcsv(trim($lines[$i]));\n        if (count($fields) != count($header)) {\n            continue;\n        }\n        $row = array_combine($header, $fields);\n        $row[\"id\"] = (int)$row[\"id\"];\n        $row[\"units\"] = (int)$row[\"units\"];\n        $row[\"price\"] = $row[\"price\"] === \"\" ? null : (float)$row[\"price\"];\n        $rows[] = $row;\n    }\n    return $rows;\n}\n\nfunction row_count($file = \"data.csv\") {\n    return count(load_sales($file));\n}\n\nfunction find_by_id($id, $file = \"data.csv\") {\n    foreach (load_sales($file) as $row) {\n        if ($row[\"id\"] == $id) {\n            return $row;\n        }\n    }\n    throw new InvalidArgumentException(\"No row with id \" . $id);\n}\n\nfunction row_revenue($row) {\n    if ($row[\"price\"] === null || $row[\"units\"] < 0) {\n        return 0;\n    }\n    return round($row[\"units\"] * $row[\"price\"], 2);\n}\n\nfunction total_revenue($file = \"data.csv\") {\n    $sum = 0;\n    foreach (load_sales($file) as $row) {\n        $sum += row_revenue($row);\n    }\n    return round($sum, 2);\n}\n\nfunction revenue_by_region($file = \"data.csv\") {\n    $totals = array();\n    foreach (load_sales($file) as $row) {\n        $region = $row[\"region\"];\n        if (!isset($totals[$region])) {\n            $totals[$region] = 0;\n        }\n        $totals[$region] += row_revenue($row);\n    }\n    ksort($totals);\n    foreach ($totals as $k => $v) {\n        $totals[$k] = round($v, 2);\n    }\n    return $totals;\n}\n\nfunction names_in_region($region, $file = \"data.csv\") {\n    $names = array();\n    foreach (load_sales($file) as $row) {\n        if ($row[\"region\"] === $region) {\n            $names[] = $row[\"name\"];\n        }\n    }\n    return $names;\n}\n\nfunction top_sellers($n, $file = \"data.csv\") {\n    if ($n < 1) {\n        throw new InvalidArgumentException(\"n must be at least 1\");\n    }\n    $rows = load_sales($file);\n    usort($rows, function ($a, $b) {\n        $ra = row_revenue($a);\n        $rb = row_revenue($b);\n        if ($ra == $rb) {\n            return $a[\"id\"] - $b[\"id\"];\n        }\n        return $ra < $rb ? 1 : -1;\n    });\n    $names = array();\n    foreach (array_slice($rows, 0, $n) as $row) {\n        $names[] = $row[\"name\"];\n    }\n    return $names;\n}\n\nfunction rows_missing_price($file = \"data.csv\") {\n    $ids = array();\n    foreach (load_sales($file) as $row) {\n        if ($row[\"price\"] === null) {\n            $ids[] = $row[\"id\"];\n        }\n    }\n    return $ids;\n}\n\nfunction average_units($file = \"data.csv\") {\n    $rows = load_sales($file);\n    if (count($rows) == 0) {\n        return 0;\n    }\n    $sum = 0;\n    foreach ($rows as $row) {\n        $sum += $row[\"units\"];\n    }\n    return round($sum / count($rows), 2);\n}\n\nfunction report_line($id, $file = \"data.csv\") {\n    $row = find_by_id($id, $file);\n    return sprintf(\"#%d %s (%s): %d units, revenue %.2f\", $row[\"id\"], $row[\"name\"], $row[\"region\"], $row[\"units\"], row_revenue($row));\n}\n",
      "migrated_python": "import os\nimport csv\nfrom typing import List, Dict, Any, Optional\n\n# Helper to get file path\n\ndef _file_path(file: str = \"data.csv\") -> str:\n    return os.path.join(os.path.dirname(__file__), file)\n\n# Load sales data\n\ndef load_sales(file: str = \"data.csv\") -> List[Dict[str, Any]]:\n    path = _file_path(file)\n    if not os.path.isfile(path):\n        raise RuntimeError(f\"File not found: {file}\")\n    with open(path, newline='', encoding='utf-8') as f:\n        reader = csv.reader(f)\n        rows = list(reader)\n    if not rows:\n        return []\n    header = [h.strip() for h in rows[0]]\n    sales: List[Dict[str, Any]] = []\n    for line in rows[1:]:\n        if not line:\n            continue\n        if len(line) != len(header):\n            continue\n        record = dict(zip(header, [x.strip() for x in line]))\n        try:\n            record[\"id\"] = int(record[\"id\"])\n            record[\"units\"] = int(record[\"units\"])\n        except (ValueError, KeyError):\n            continue\n        price_str = record.get(\"price\", \"\")\n        record[\"price\"] = None if price_str == \"\" else float(price_str)\n        sales.append(record)\n    return sales\n\n# Row count\n\ndef row_count(file: str = \"data.csv\") -> int:\n    return len(load_sales(file))\n\n# Find by id\n\ndef find_by_id(id: int, file: str = \"data.csv\") -> Dict[str, Any]:\n    for row in load_sales(file):\n        if row.get(\"id\") == id:\n            return row\n    raise ValueError(f\"No row with id {id}\")\n\n# Row revenue\n\ndef row_revenue(row: Dict[str, Any]) -> float:\n    price = row.get(\"price\")\n    units = row.get(\"units\", 0)\n    if price is None or units < 0:\n        return 0.0\n    return round(units * price, 2)\n\n# Total revenue\n\ndef total_revenue(file: str = \"data.csv\") -> float:\n    total = 0.0\n    for row in load_sales(file):\n        total += row_revenue(row)\n    return round(total, 2)\n\n# Revenue by region\n\ndef revenue_by_region(file: str = \"data.csv\") -> Dict[str, float]:\n    totals: Dict[str, float] = {}\n    for row in load_sales(file):\n        region = row.get(\"region\", \"\")\n        rev = row_revenue(row)\n        totals[region] = totals.get(region, 0.0) + rev\n    # sort keys\n    sorted_totals = {k: round(v, 2) for k, v in sorted(totals.items())}\n    return sorted_totals\n\n# Names in region\n\ndef names_in_region(region: str, file: str = \"data.csv\") -> List[str]:\n    names: List[str] = []\n    for row in load_sales(file):\n        if row.get(\"region\") == region:\n            names.append(row.get(\"name\", \"\"))\n    return names\n\n# Top sellers\n\ndef top_sellers(n: int, file: str = \"data.csv\") -> List[str]:\n    if n < 1:\n        raise ValueError(\"n must be at least 1\")\n    rows = load_sales(file)\n    def sort_key(r: Dict[str, Any]):\n        rev = row_revenue(r)\n        return (-rev, r.get(\"id\", 0))\n    rows_sorted = sorted(rows, key=sort_key)\n    top_rows = rows_sorted[:n]\n    return [r.get(\"name\", \"\") for r in top_rows]\n\n# Rows missing price\n\ndef rows_missing_price(file: str = \"data.csv\") -> List[int]:\n    ids: List[int] = []\n    for row in load_sales(file):\n        if row.get(\"price\") is None:\n            ids.append(row.get(\"id\"))\n    return ids\n\n# Average units\n\ndef average_units(file: str = \"data.csv\") -> float:\n    rows = load_sales(file)\n    if not rows:\n        return 0.0\n    total_units = sum(row.get(\"units\", 0) for row in rows)\n    return round(total_units / len(rows), 2)\n\n# Report line\n\ndef report_line(id: int, file: str = \"data.csv\") -> str:\n    row = find_by_id(id, file)\n    return f\"#{row['id']} {row['name']} ({row['region']}): {row['units']} units, revenue {row_revenue(row):.2f}\"\n",
      "explanation": "Converted each PHP function into a Python function preserving signatures, types, and behavior. Used the csv module for parsing. Handled file paths relative to the script directory. Implemented rounding with Python's round() to match PHP's round() semantics. Exceptions mapped to RuntimeError for file missing, ValueError for invalid arguments or missing IDs. All functions return values, no I/O at module level.",
      "assumptions": [
        "CSV uses comma as separator and UTF\u20118 encoding.",
        "Empty or missing values are handled as None or empty strings. ",
        "Price values are convertible to float; invalid conversions skip the row. ",
        "Integer fields are convertible to int; invalid conversions skip the row. ",
        "Row order after sorting top_sellers follows descending revenue, then ascending id.",
        "The report_line function formats revenue with two decimal places.",
        ""
      ],
      "warnings": [
        "Functions raise ValueError for missing IDs or invalid arguments, mirroring PHP exceptions."
      ],
      "functions": [
        {
          "function": "average_units",
          "verdict": "MISMATCH",
          "total": 2,
          "matched": 1,
          "failures": [
            {
              "args": [],
              "legacy": {
                "function": "average_units",
                "args": [],
                "value": 6.88,
                "ok": true
              },
              "migrated": {
                "function": "average_units",
                "args": [],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "find_by_id",
          "verdict": "MISMATCH",
          "total": 5,
          "matched": 1,
          "failures": [
            {
              "args": [
                1
              ],
              "legacy": {
                "function": "find_by_id",
                "args": [
                  1
                ],
                "value": {
                  "id": 1,
                  "name": "Alpha Kit",
                  "region": "north",
                  "units": 10,
                  "price": 2.5
                },
                "ok": true
              },
              "migrated": {
                "function": "find_by_id",
                "args": [
                  1
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                2
              ],
              "legacy": {
                "function": "find_by_id",
                "args": [
                  2
                ],
                "value": {
                  "id": 2,
                  "name": "Beta, Large",
                  "region": "south",
                  "units": 5,
                  "price": 19.99
                },
                "ok": true
              },
              "migrated": {
                "function": "find_by_id",
                "args": [
                  2
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                5
              ],
              "legacy": {
                "function": "find_by_id",
                "args": [
                  5
                ],
                "value": {
                  "id": 5,
                  "name": "Epsilon",
                  "region": "south",
                  "units": 7,
                  "price": null
                },
                "ok": true
              },
              "migrated": {
                "function": "find_by_id",
                "args": [
                  5
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "names_in_region",
          "verdict": "MISMATCH",
          "total": 4,
          "matched": 0,
          "failures": [
            {
              "args": [
                "north"
              ],
              "legacy": {
                "function": "names_in_region",
                "args": [
                  "north"
                ],
                "value": [
                  "Alpha Kit",
                  "Gamma",
                  "Eta"
                ],
                "ok": true
              },
              "migrated": {
                "function": "names_in_region",
                "args": [
                  "north"
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                "south"
              ],
              "legacy": {
                "function": "names_in_region",
                "args": [
                  "south"
                ],
                "value": [
                  "Beta, Large",
                  "Epsilon"
                ],
                "ok": true
              },
              "migrated": {
                "function": "names_in_region",
                "args": [
                  "south"
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                "North"
              ],
              "legacy": {
                "function": "names_in_region",
                "args": [
                  "North"
                ],
                "value": [],
                "ok": true
              },
              "migrated": {
                "function": "names_in_region",
                "args": [
                  "North"
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "report_line",
          "verdict": "MISMATCH",
          "total": 5,
          "matched": 1,
          "failures": [
            {
              "args": [
                2
              ],
              "legacy": {
                "function": "report_line",
                "args": [
                  2
                ],
                "value": "#2 Beta, Large (south): 5 units, revenue 99.95",
                "ok": true
              },
              "migrated": {
                "function": "report_line",
                "args": [
                  2
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                3
              ],
              "legacy": {
                "function": "report_line",
                "args": [
                  3
                ],
                "value": "#3 Gamma (north): 0 units, revenue 0.00",
                "ok": true
              },
              "migrated": {
                "function": "report_line",
                "args": [
                  3
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                5
              ],
              "legacy": {
                "function": "report_line",
                "args": [
                  5
                ],
                "value": "#5 Epsilon (south): 7 units, revenue 0.00",
                "ok": true
              },
              "migrated": {
                "function": "report_line",
                "args": [
                  5
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "revenue_by_region",
          "verdict": "MISMATCH",
          "total": 1,
          "matched": 0,
          "failures": [
            {
              "args": [],
              "legacy": {
                "function": "revenue_by_region",
                "args": [],
                "value": {
                  "east": 337.2,
                  "north": 46.0,
                  "south": 99.95,
                  "west": 0.0
                },
                "ok": true
              },
              "migrated": {
                "function": "revenue_by_region",
                "args": [],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "row_count",
          "verdict": "MISMATCH",
          "total": 3,
          "matched": 1,
          "failures": [
            {
              "args": [],
              "legacy": {
                "function": "row_count",
                "args": [],
                "value": 8,
                "ok": true
              },
              "migrated": {
                "function": "row_count",
                "args": [],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                "data.csv"
              ],
              "legacy": {
                "function": "row_count",
                "args": [
                  "data.csv"
                ],
                "value": 8,
                "ok": true
              },
              "migrated": {
                "function": "row_count",
                "args": [
                  "data.csv"
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "row_revenue",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "rows_missing_price",
          "verdict": "MISMATCH",
          "total": 1,
          "matched": 0,
          "failures": [
            {
              "args": [],
              "legacy": {
                "function": "rows_missing_price",
                "args": [],
                "value": [
                  5
                ],
                "ok": true
              },
              "migrated": {
                "function": "rows_missing_price",
                "args": [],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "top_sellers",
          "verdict": "MISMATCH",
          "total": 4,
          "matched": 1,
          "failures": [
            {
              "args": [
                1
              ],
              "legacy": {
                "function": "top_sellers",
                "args": [
                  1
                ],
                "value": [
                  "Theta"
                ],
                "ok": true
              },
              "migrated": {
                "function": "top_sellers",
                "args": [
                  1
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                3
              ],
              "legacy": {
                "function": "top_sellers",
                "args": [
                  3
                ],
                "value": [
                  "Theta",
                  "Beta, Large",
                  "Delta"
                ],
                "ok": true
              },
              "migrated": {
                "function": "top_sellers",
                "args": [
                  3
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            },
            {
              "args": [
                100
              ],
              "legacy": {
                "function": "top_sellers",
                "args": [
                  100
                ],
                "value": [
                  "Theta",
                  "Beta, Large",
                  "Delta",
                  "Alpha Kit",
                  "Eta",
                  "Gamma",
                  "Epsilon",
                  "Zeta"
                ],
                "ok": true
              },
              "migrated": {
                "function": "top_sellers",
                "args": [
                  100
                ],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        },
        {
          "function": "total_revenue",
          "verdict": "MISMATCH",
          "total": 1,
          "matched": 0,
          "failures": [
            {
              "args": [],
              "legacy": {
                "function": "total_revenue",
                "args": [],
                "value": 483.15,
                "ok": true
              },
              "migrated": {
                "function": "total_revenue",
                "args": [],
                "ok": false,
                "error": "RuntimeError: File not found: data.csv"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "07_unsafe_input",
      "counted": true,
      "model": "openai/gpt-oss-20b",
      "tokens": 1252,
      "generation_status": "generated",
      "comparison_status": "compared",
      "legacy_php": "// ===== FILE: legacy.php =====\n<?php\n// Unsafe input program. TWO deliberate vulnerabilities (the project's examples):\n//   1. user input is put into HTML without escaping (XSS)\n//   2. user input is glued into a shell command (command injection)\n\nfunction greeting_html($name) {\n    return \"<h1>Hello \" . $name . \"</h1>\";\n}\n\nfunction comment_html($author, $text) {\n    return \"<div class=\\\"comment\\\"><b>\" . $author . \"</b>: \" . $text . \"</div>\";\n}\n\nfunction search_results_html($query, $count) {\n    $html = \"<p>You searched for: \" . $query . \"</p>\";\n    if ($count == 0) {\n        $html .= \"<p>No results.</p>\";\n    } else {\n        $html .= \"<p>\" . $count . \" results found.</p>\";\n    }\n    return $html;\n}\n\n// SAFE version for comparison (escapes the input).\nfunction greeting_html_safe($name) {\n    return \"<h1>Hello \" . htmlspecialchars($name, ENT_QUOTES, \"UTF-8\") . \"</h1>\";\n}\n\n// VULNERABLE ON PURPOSE: input is glued into a shell command.\nfunction echo_message($message) {\n    $output = array();\n    exec(\"echo Message: \" . $message . \" 2>&1\", $output);\n    return $output;\n}\n\n// VULNERABLE ON PURPOSE: input is glued into a shell command.\nfunction count_words_shell($text) {\n    $result = shell_exec(\"echo \" . $text . \" | wc -w\");\n    return (int)trim($result);\n}\n\nfunction clean_filename($name) {\n    return preg_replace(\"/[^A-Za-z0-9._-]/\", \"_\", $name);\n}\n\nfunction is_valid_username($name) {\n    return preg_match(\"/^[a-z][a-z0-9_]{2,15}$/\", $name) === 1;\n}\n",
      "migrated_python": "import re\nimport html\nimport subprocess\n\ndef greeting_html(name: str) -> str:\n    return f\"<h1>Hello {name}</h1>\"\n\ndef comment_html(author: str, text: str) -> str:\n    return f\"<div class=\\\"comment\\\"><b>{author}</b>: {text}</div>\"\n\ndef search_results_html(query: str, count: int) -> str:\n    html_part = f\"<p>You searched for: {query}</p>\"\n    if count == 0:\n        html_part += \"<p>No results.</p>\"\n    else:\n        html_part += f\"<p>{count} results found.</p>\"\n    return html_part\n\n# SAFE version for comparison (escapes the input).\n\ndef greeting_html_safe(name: str) -> str:\n    escaped = html.escape(name, quote=True)\n    return f\"<h1>Hello {escaped}</h1>\"\n\n# VULNERABLE ON PURPOSE: input is glued into a shell command.\n\ndef echo_message(message: str) -> list:\n    # In PHP, exec returns an array of lines. We mimic that.\n    cmd = f\"echo Message: {message} 2>&1\"\n    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)\n    # split output into lines, strip trailing newlines\n    return completed.stdout.splitlines()\n\n# VULNERABLE ON PURPOSE: input is glued into a shell command.\n\ndef count_words_shell(text: str) -> int:\n    cmd = f\"echo {text} | wc -w\"\n    result = subprocess.check_output(cmd, shell=True, text=True)\n    return int(result.strip())\n\ndef clean_filename(name: str) -> str:\n    return re.sub(r\"[^A-Za-z0-9._-]\", \"_\", name)\n\ndef is_valid_username(name: str) -> bool:\n    return re.match(r\"^[a-z][a-z0-9_]{2,15}$\", name) is not None\n",
      "explanation": "The Python module reproduces each PHP function\u2019s behaviour. String concatenation and formatting use f-strings, regex patterns are identical, and shell interactions use subprocess with the same command strings. The escaping helper uses html.escape. All functions return the expected values without side effects like printing.",
      "assumptions": [
        "The input types are always strings or ints as in the original PHP functions.",
        "Subprocess output encoding matches UTF-8, matching PHP\u2019s default.",
        "The environment allows shell execution; no sandbox restrictions are applied.",
        "PHP\u2019s exec returns an array of lines; this is emulated by splitting stdout on newlines."
      ],
      "warnings": [
        "The echo_message and count_words_shell functions are intentionally vulnerable to command injection, mirroring the original PHP code."
      ],
      "functions": [
        {
          "function": "clean_filename",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        },
        {
          "function": "comment_html",
          "verdict": "EQUIVALENT",
          "total": 2,
          "matched": 2,
          "failures": []
        },
        {
          "function": "count_words_shell",
          "verdict": "MISMATCH",
          "total": 3,
          "matched": 0,
          "failures": [
            {
              "args": [
                "one two three"
              ],
              "legacy": {
                "function": "count_words_shell",
                "args": [
                  "one two three"
                ],
                "value": 3,
                "ok": true
              },
              "migrated": {
                "function": "count_words_shell",
                "args": [
                  "one two three"
                ],
                "ok": false,
                "error": "CalledProcessError: Command 'echo one two three | wc -w' returned non-zero exit status 255."
              }
            },
            {
              "args": [
                ""
              ],
              "legacy": {
                "function": "count_words_shell",
                "args": [
                  ""
                ],
                "value": 0,
                "ok": true
              },
              "migrated": {
                "function": "count_words_shell",
                "args": [
                  ""
                ],
                "ok": false,
                "error": "CalledProcessError: Command 'echo  | wc -w' returned non-zero exit status 255."
              }
            },
            {
              "args": [
                "hello; echo extra words here"
              ],
              "legacy": {
                "function": "count_words_shell",
                "args": [
                  "hello; echo extra words here"
                ],
                "value": 0,
                "ok": true
              },
              "migrated": {
                "function": "count_words_shell",
                "args": [
                  "hello; echo extra words here"
                ],
                "ok": false,
                "error": "CalledProcessError: Command 'echo hello; echo extra words here | wc -w' returned non-zero exit status 255."
              }
            }
          ]
        },
        {
          "function": "echo_message",
          "verdict": "MISMATCH",
          "total": 7,
          "matched": 0,
          "failures": [
            {
              "args": [
                "hello"
              ],
              "legacy": {
                "function": "echo_message",
                "args": [
                  "hello"
                ],
                "value": [
                  "Message: hello"
                ],
                "ok": true
              },
              "migrated": {
                "function": "echo_message",
                "args": [
                  "hello"
                ],
                "ok": true,
                "value": [
                  "Message: hello "
                ]
              }
            },
            {
              "args": [
                ""
              ],
              "legacy": {
                "function": "echo_message",
                "args": [
                  ""
                ],
                "value": [
                  "Message:"
                ],
                "ok": true
              },
              "migrated": {
                "function": "echo_message",
                "args": [
                  ""
                ],
                "ok": true,
                "value": [
                  "Message:  "
                ]
              }
            },
            {
              "args": [
                "one two three"
              ],
              "legacy": {
                "function": "echo_message",
                "args": [
                  "one two three"
                ],
                "value": [
                  "Message: one two three"
                ],
                "ok": true
              },
              "migrated": {
                "function": "echo_message",
                "args": [
                  "one two three"
                ],
                "ok": true,
                "value": [
                  "Message: one two three "
                ]
              }
            }
          ]
        },
        {
          "function": "greeting_html",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "greeting_html_safe",
          "verdict": "MISMATCH",
          "total": 2,
          "matched": 1,
          "failures": [
            {
              "args": [
                "O'Brien \"Bob\""
              ],
              "legacy": {
                "function": "greeting_html_safe",
                "args": [
                  "O'Brien \"Bob\""
                ],
                "value": "<h1>Hello O&#039;Brien &quot;Bob&quot;</h1>",
                "ok": true
              },
              "migrated": {
                "function": "greeting_html_safe",
                "args": [
                  "O'Brien \"Bob\""
                ],
                "ok": true,
                "value": "<h1>Hello O&#x27;Brien &quot;Bob&quot;</h1>"
              }
            }
          ]
        },
        {
          "function": "is_valid_username",
          "verdict": "EQUIVALENT",
          "total": 5,
          "matched": 5,
          "failures": []
        },
        {
          "function": "search_results_html",
          "verdict": "EQUIVALENT",
          "total": 3,
          "matched": 3,
          "failures": []
        }
      ]
    }
  ]
};
