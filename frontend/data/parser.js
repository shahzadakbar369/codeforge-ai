window.CODEFORGE_PARSER = {
  "generated_on": "2026-11-15",
  "programs": [
    {
      "program": "01_calculator",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "add",
            "subtract",
            "multiply",
            "divide",
            "modulo",
            "power",
            "percent_of",
            "average",
            "clamp",
            "is_even",
            "round_to",
            "celsius_to_fahrenheit",
            "factorial"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "add",
          "file": "legacy.php",
          "params": [
            "$a",
            "$b"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "subtract",
          "file": "legacy.php",
          "params": [
            "$a",
            "$b"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "multiply",
          "file": "legacy.php",
          "params": [
            "$a",
            "$b"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "divide",
          "file": "legacy.php",
          "params": [
            "$a",
            "$b"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "modulo",
          "file": "legacy.php",
          "params": [
            "$a",
            "$b"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "power",
          "file": "legacy.php",
          "params": [
            "$base",
            "$exp"
          ],
          "calls": [],
          "external_calls": [
            "pow"
          ],
          "risky_calls": []
        },
        {
          "name": "percent_of",
          "file": "legacy.php",
          "params": [
            "$percent",
            "$value"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "average",
          "file": "legacy.php",
          "params": [
            "$numbers"
          ],
          "calls": [],
          "external_calls": [
            "array_sum",
            "count"
          ],
          "risky_calls": []
        },
        {
          "name": "clamp",
          "file": "legacy.php",
          "params": [
            "$x",
            "$lo",
            "$hi"
          ],
          "calls": [],
          "external_calls": [
            "max",
            "min"
          ],
          "risky_calls": []
        },
        {
          "name": "is_even",
          "file": "legacy.php",
          "params": [
            "$n"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "round_to",
          "file": "legacy.php",
          "params": [
            "$x",
            "$places"
          ],
          "calls": [],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "celsius_to_fahrenheit",
          "file": "legacy.php",
          "params": [
            "$c"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "factorial",
          "file": "legacy.php",
          "params": [
            "$n"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        }
      ],
      "edges": [],
      "warnings": []
    },
    {
      "program": "02_student_grading",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "calculate_average",
            "letter_grade",
            "grade_points",
            "gpa",
            "weighted_grade",
            "count_passing",
            "grade_distribution",
            "highest_score",
            "rank_scores",
            "curve_scores",
            "is_honor_roll"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "calculate_average",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [],
          "external_calls": [
            "array_sum",
            "count",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "letter_grade",
          "file": "legacy.php",
          "params": [
            "$score"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "grade_points",
          "file": "legacy.php",
          "params": [
            "$letter"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "gpa",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [
            "grade_points",
            "letter_grade"
          ],
          "external_calls": [
            "count",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "weighted_grade",
          "file": "legacy.php",
          "params": [
            "$scores",
            "$weights"
          ],
          "calls": [],
          "external_calls": [
            "array_sum",
            "count",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "count_passing",
          "file": "legacy.php",
          "params": [
            "$scores",
            "$pass_mark"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "grade_distribution",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [
            "letter_grade"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "highest_score",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [],
          "external_calls": [
            "count",
            "max"
          ],
          "risky_calls": []
        },
        {
          "name": "rank_scores",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [],
          "external_calls": [
            "rsort"
          ],
          "risky_calls": []
        },
        {
          "name": "curve_scores",
          "file": "legacy.php",
          "params": [
            "$scores",
            "$bonus"
          ],
          "calls": [],
          "external_calls": [
            "min"
          ],
          "risky_calls": []
        },
        {
          "name": "is_honor_roll",
          "file": "legacy.php",
          "params": [
            "$scores"
          ],
          "calls": [
            "calculate_average"
          ],
          "external_calls": [
            "min"
          ],
          "risky_calls": []
        }
      ],
      "edges": [
        {
          "from": "gpa",
          "to": "grade_points"
        },
        {
          "from": "gpa",
          "to": "letter_grade"
        },
        {
          "from": "grade_distribution",
          "to": "letter_grade"
        },
        {
          "from": "is_honor_roll",
          "to": "calculate_average"
        }
      ],
      "warnings": []
    },
    {
      "program": "03_invoice",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "line_total",
            "invoice_subtotal",
            "tax_for_amount",
            "shipping_cost",
            "late_fee",
            "format_invoice_number",
            "invoice_total",
            "split_payment"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "line_total",
          "file": "legacy.php",
          "params": [
            "$price",
            "$qty",
            "$discount_percent"
          ],
          "calls": [],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "invoice_subtotal",
          "file": "legacy.php",
          "params": [
            "$items"
          ],
          "calls": [
            "line_total"
          ],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "tax_for_amount",
          "file": "legacy.php",
          "params": [
            "$amount"
          ],
          "calls": [],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "shipping_cost",
          "file": "legacy.php",
          "params": [
            "$weight_kg"
          ],
          "calls": [],
          "external_calls": [
            "ceil"
          ],
          "risky_calls": []
        },
        {
          "name": "late_fee",
          "file": "legacy.php",
          "params": [
            "$amount",
            "$days_late"
          ],
          "calls": [],
          "external_calls": [
            "ceil",
            "min",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "format_invoice_number",
          "file": "legacy.php",
          "params": [
            "$n"
          ],
          "calls": [],
          "external_calls": [
            "sprintf"
          ],
          "risky_calls": []
        },
        {
          "name": "invoice_total",
          "file": "legacy.php",
          "params": [
            "$items",
            "$shipping_weight"
          ],
          "calls": [
            "invoice_subtotal",
            "shipping_cost",
            "tax_for_amount"
          ],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "split_payment",
          "file": "legacy.php",
          "params": [
            "$total",
            "$installments"
          ],
          "calls": [],
          "external_calls": [
            "array_fill",
            "floor",
            "round"
          ],
          "risky_calls": []
        }
      ],
      "edges": [
        {
          "from": "invoice_subtotal",
          "to": "line_total"
        },
        {
          "from": "invoice_total",
          "to": "invoice_subtotal"
        },
        {
          "from": "invoice_total",
          "to": "shipping_cost"
        },
        {
          "from": "invoice_total",
          "to": "tax_for_amount"
        }
      ],
      "warnings": []
    },
    {
      "program": "04_payroll",
      "files": [
        {
          "file": "helpers.php",
          "functions": [
            "round_money",
            "format_money",
            "overtime_hours",
            "income_tax"
          ],
          "includes": []
        },
        {
          "file": "legacy.php",
          "functions": [
            "__construct",
            "regular_pay",
            "overtime_pay",
            "bonus",
            "gross_pay",
            "tax",
            "net_pay",
            "employee_from_array",
            "employee_gross",
            "employee_net",
            "employee_payslip",
            "payslip_line",
            "payroll_total",
            "highest_paid",
            "department_summary"
          ],
          "includes": [
            "/helpers.php"
          ]
        }
      ],
      "functions": [
        {
          "name": "round_money",
          "file": "helpers.php",
          "params": [
            "$amount"
          ],
          "calls": [],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "format_money",
          "file": "helpers.php",
          "params": [
            "$amount"
          ],
          "calls": [],
          "external_calls": [
            "number_format"
          ],
          "risky_calls": []
        },
        {
          "name": "overtime_hours",
          "file": "helpers.php",
          "params": [
            "$hours",
            "$threshold"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "income_tax",
          "file": "helpers.php",
          "params": [
            "$gross"
          ],
          "calls": [
            "round_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "__construct",
          "file": "legacy.php",
          "params": [
            "$name",
            "$rate",
            "$hours",
            "$is_manager"
          ],
          "calls": [],
          "external_calls": [
            "trim"
          ],
          "risky_calls": []
        },
        {
          "name": "regular_pay",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "round_money"
          ],
          "external_calls": [
            "min"
          ],
          "risky_calls": []
        },
        {
          "name": "overtime_pay",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "overtime_hours",
            "round_money"
          ],
          "external_calls": [
            "min"
          ],
          "risky_calls": []
        },
        {
          "name": "bonus",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "round_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "gross_pay",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "round_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "tax",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "income_tax"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "net_pay",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "round_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "employee_from_array",
          "file": "legacy.php",
          "params": [
            "$emp"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "employee_gross",
          "file": "legacy.php",
          "params": [
            "$name",
            "$rate",
            "$hours",
            "$is_manager"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "employee_net",
          "file": "legacy.php",
          "params": [
            "$name",
            "$rate",
            "$hours",
            "$is_manager"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "employee_payslip",
          "file": "legacy.php",
          "params": [
            "$name",
            "$rate",
            "$hours",
            "$is_manager"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "payslip_line",
          "file": "legacy.php",
          "params": [
            "$name",
            "$rate",
            "$hours",
            "$is_manager"
          ],
          "calls": [
            "employee_payslip",
            "format_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "payroll_total",
          "file": "legacy.php",
          "params": [
            "$employees"
          ],
          "calls": [
            "employee_from_array",
            "round_money"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "highest_paid",
          "file": "legacy.php",
          "params": [
            "$employees"
          ],
          "calls": [
            "employee_from_array"
          ],
          "external_calls": [
            "count"
          ],
          "risky_calls": []
        },
        {
          "name": "department_summary",
          "file": "legacy.php",
          "params": [
            "$employees"
          ],
          "calls": [
            "employee_from_array",
            "round_money"
          ],
          "external_calls": [
            "count"
          ],
          "risky_calls": []
        }
      ],
      "edges": [
        {
          "from": "income_tax",
          "to": "round_money"
        },
        {
          "from": "regular_pay",
          "to": "round_money"
        },
        {
          "from": "overtime_pay",
          "to": "overtime_hours"
        },
        {
          "from": "overtime_pay",
          "to": "round_money"
        },
        {
          "from": "bonus",
          "to": "round_money"
        },
        {
          "from": "gross_pay",
          "to": "round_money"
        },
        {
          "from": "tax",
          "to": "income_tax"
        },
        {
          "from": "net_pay",
          "to": "round_money"
        },
        {
          "from": "payslip_line",
          "to": "employee_payslip"
        },
        {
          "from": "payslip_line",
          "to": "format_money"
        },
        {
          "from": "payroll_total",
          "to": "employee_from_array"
        },
        {
          "from": "payroll_total",
          "to": "round_money"
        },
        {
          "from": "highest_paid",
          "to": "employee_from_array"
        },
        {
          "from": "department_summary",
          "to": "employee_from_array"
        },
        {
          "from": "department_summary",
          "to": "round_money"
        }
      ],
      "warnings": []
    },
    {
      "program": "05_inventory",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "get_db",
            "seed_db",
            "reset_inventory",
            "count_products",
            "get_product",
            "find_products_by_name",
            "products_in_category",
            "add_stock",
            "remove_stock",
            "low_stock",
            "inventory_value",
            "apply_discount",
            "category_summary"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "get_db",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "seed_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "seed_db",
          "file": "legacy.php",
          "params": [
            "$db"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "reset_inventory",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "count_products",
            "get_db",
            "seed_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "count_products",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "get_product",
          "file": "legacy.php",
          "params": [
            "$id"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "find_products_by_name",
          "file": "legacy.php",
          "params": [
            "$name"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "products_in_category",
          "file": "legacy.php",
          "params": [
            "$category"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "add_stock",
          "file": "legacy.php",
          "params": [
            "$id",
            "$qty"
          ],
          "calls": [
            "get_db",
            "get_product"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "remove_stock",
          "file": "legacy.php",
          "params": [
            "$id",
            "$qty"
          ],
          "calls": [
            "get_db",
            "get_product"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "low_stock",
          "file": "legacy.php",
          "params": [
            "$threshold"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "inventory_value",
          "file": "legacy.php",
          "params": [
            "$category"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "apply_discount",
          "file": "legacy.php",
          "params": [
            "$category",
            "$percent"
          ],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "category_summary",
          "file": "legacy.php",
          "params": [],
          "calls": [
            "get_db"
          ],
          "external_calls": [],
          "risky_calls": []
        }
      ],
      "edges": [
        {
          "from": "get_db",
          "to": "seed_db"
        },
        {
          "from": "reset_inventory",
          "to": "count_products"
        },
        {
          "from": "reset_inventory",
          "to": "get_db"
        },
        {
          "from": "reset_inventory",
          "to": "seed_db"
        },
        {
          "from": "count_products",
          "to": "get_db"
        },
        {
          "from": "get_product",
          "to": "get_db"
        },
        {
          "from": "find_products_by_name",
          "to": "get_db"
        },
        {
          "from": "products_in_category",
          "to": "get_db"
        },
        {
          "from": "add_stock",
          "to": "get_db"
        },
        {
          "from": "add_stock",
          "to": "get_product"
        },
        {
          "from": "remove_stock",
          "to": "get_db"
        },
        {
          "from": "remove_stock",
          "to": "get_product"
        },
        {
          "from": "low_stock",
          "to": "get_db"
        },
        {
          "from": "inventory_value",
          "to": "get_db"
        },
        {
          "from": "apply_discount",
          "to": "get_db"
        },
        {
          "from": "category_summary",
          "to": "get_db"
        }
      ],
      "warnings": []
    },
    {
      "program": "06_csv_report",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "load_sales",
            "row_count",
            "find_by_id",
            "row_revenue",
            "total_revenue",
            "revenue_by_region",
            "names_in_region",
            "top_sellers",
            "rows_missing_price",
            "average_units",
            "report_line"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "load_sales",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [],
          "external_calls": [
            "array_combine",
            "count",
            "file",
            "file_exists",
            "str_getcsv",
            "trim"
          ],
          "risky_calls": []
        },
        {
          "name": "row_count",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [
            "load_sales"
          ],
          "external_calls": [
            "count"
          ],
          "risky_calls": []
        },
        {
          "name": "find_by_id",
          "file": "legacy.php",
          "params": [
            "$id",
            "$file"
          ],
          "calls": [
            "load_sales"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "row_revenue",
          "file": "legacy.php",
          "params": [
            "$row"
          ],
          "calls": [],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "total_revenue",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [
            "load_sales",
            "row_revenue"
          ],
          "external_calls": [
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "revenue_by_region",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [
            "load_sales",
            "row_revenue"
          ],
          "external_calls": [
            "ksort",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "names_in_region",
          "file": "legacy.php",
          "params": [
            "$region",
            "$file"
          ],
          "calls": [
            "load_sales"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "top_sellers",
          "file": "legacy.php",
          "params": [
            "$n",
            "$file"
          ],
          "calls": [
            "load_sales",
            "row_revenue"
          ],
          "external_calls": [
            "array_slice",
            "usort"
          ],
          "risky_calls": []
        },
        {
          "name": "rows_missing_price",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [
            "load_sales"
          ],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "average_units",
          "file": "legacy.php",
          "params": [
            "$file"
          ],
          "calls": [
            "load_sales"
          ],
          "external_calls": [
            "count",
            "round"
          ],
          "risky_calls": []
        },
        {
          "name": "report_line",
          "file": "legacy.php",
          "params": [
            "$id",
            "$file"
          ],
          "calls": [
            "find_by_id",
            "row_revenue"
          ],
          "external_calls": [
            "sprintf"
          ],
          "risky_calls": []
        }
      ],
      "edges": [
        {
          "from": "row_count",
          "to": "load_sales"
        },
        {
          "from": "find_by_id",
          "to": "load_sales"
        },
        {
          "from": "total_revenue",
          "to": "load_sales"
        },
        {
          "from": "total_revenue",
          "to": "row_revenue"
        },
        {
          "from": "revenue_by_region",
          "to": "load_sales"
        },
        {
          "from": "revenue_by_region",
          "to": "row_revenue"
        },
        {
          "from": "names_in_region",
          "to": "load_sales"
        },
        {
          "from": "top_sellers",
          "to": "load_sales"
        },
        {
          "from": "top_sellers",
          "to": "row_revenue"
        },
        {
          "from": "rows_missing_price",
          "to": "load_sales"
        },
        {
          "from": "average_units",
          "to": "load_sales"
        },
        {
          "from": "report_line",
          "to": "find_by_id"
        },
        {
          "from": "report_line",
          "to": "row_revenue"
        }
      ],
      "warnings": []
    },
    {
      "program": "07_unsafe_input",
      "files": [
        {
          "file": "legacy.php",
          "functions": [
            "greeting_html",
            "comment_html",
            "search_results_html",
            "greeting_html_safe",
            "echo_message",
            "count_words_shell",
            "clean_filename",
            "is_valid_username"
          ],
          "includes": []
        }
      ],
      "functions": [
        {
          "name": "greeting_html",
          "file": "legacy.php",
          "params": [
            "$name"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "comment_html",
          "file": "legacy.php",
          "params": [
            "$author",
            "$text"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "search_results_html",
          "file": "legacy.php",
          "params": [
            "$query",
            "$count"
          ],
          "calls": [],
          "external_calls": [],
          "risky_calls": []
        },
        {
          "name": "greeting_html_safe",
          "file": "legacy.php",
          "params": [
            "$name"
          ],
          "calls": [],
          "external_calls": [
            "htmlspecialchars"
          ],
          "risky_calls": []
        },
        {
          "name": "echo_message",
          "file": "legacy.php",
          "params": [
            "$message"
          ],
          "calls": [],
          "external_calls": [
            "exec"
          ],
          "risky_calls": [
            "exec"
          ]
        },
        {
          "name": "count_words_shell",
          "file": "legacy.php",
          "params": [
            "$text"
          ],
          "calls": [],
          "external_calls": [
            "shell_exec",
            "trim"
          ],
          "risky_calls": [
            "shell_exec"
          ]
        },
        {
          "name": "clean_filename",
          "file": "legacy.php",
          "params": [
            "$name"
          ],
          "calls": [],
          "external_calls": [
            "preg_replace"
          ],
          "risky_calls": []
        },
        {
          "name": "is_valid_username",
          "file": "legacy.php",
          "params": [
            "$name"
          ],
          "calls": [],
          "external_calls": [
            "preg_match"
          ],
          "risky_calls": []
        }
      ],
      "edges": [],
      "warnings": []
    }
  ]
};
