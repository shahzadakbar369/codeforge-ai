import os
import csv
from typing import List, Dict, Any, Optional

# Helper to get file path

def _file_path(file: str = "data.csv") -> str:
    return os.path.join(os.path.dirname(__file__), file)

# Load sales data

def load_sales(file: str = "data.csv") -> List[Dict[str, Any]]:
    path = _file_path(file)
    if not os.path.isfile(path):
        raise RuntimeError(f"File not found: {file}")
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    header = [h.strip() for h in rows[0]]
    sales: List[Dict[str, Any]] = []
    for line in rows[1:]:
        if not line:
            continue
        if len(line) != len(header):
            continue
        record = dict(zip(header, [x.strip() for x in line]))
        try:
            record["id"] = int(record["id"])
            record["units"] = int(record["units"])
        except (ValueError, KeyError):
            continue
        price_str = record.get("price", "")
        record["price"] = None if price_str == "" else float(price_str)
        sales.append(record)
    return sales

# Row count

def row_count(file: str = "data.csv") -> int:
    return len(load_sales(file))

# Find by id

def find_by_id(id: int, file: str = "data.csv") -> Dict[str, Any]:
    for row in load_sales(file):
        if row.get("id") == id:
            return row
    raise ValueError(f"No row with id {id}")

# Row revenue

def row_revenue(row: Dict[str, Any]) -> float:
    price = row.get("price")
    units = row.get("units", 0)
    if price is None or units < 0:
        return 0.0
    return round(units * price, 2)

# Total revenue

def total_revenue(file: str = "data.csv") -> float:
    total = 0.0
    for row in load_sales(file):
        total += row_revenue(row)
    return round(total, 2)

# Revenue by region

def revenue_by_region(file: str = "data.csv") -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for row in load_sales(file):
        region = row.get("region", "")
        rev = row_revenue(row)
        totals[region] = totals.get(region, 0.0) + rev
    # sort keys
    sorted_totals = {k: round(v, 2) for k, v in sorted(totals.items())}
    return sorted_totals

# Names in region

def names_in_region(region: str, file: str = "data.csv") -> List[str]:
    names: List[str] = []
    for row in load_sales(file):
        if row.get("region") == region:
            names.append(row.get("name", ""))
    return names

# Top sellers

def top_sellers(n: int, file: str = "data.csv") -> List[str]:
    if n < 1:
        raise ValueError("n must be at least 1")
    rows = load_sales(file)
    def sort_key(r: Dict[str, Any]):
        rev = row_revenue(r)
        return (-rev, r.get("id", 0))
    rows_sorted = sorted(rows, key=sort_key)
    top_rows = rows_sorted[:n]
    return [r.get("name", "") for r in top_rows]

# Rows missing price

def rows_missing_price(file: str = "data.csv") -> List[int]:
    ids: List[int] = []
    for row in load_sales(file):
        if row.get("price") is None:
            ids.append(row.get("id"))
    return ids

# Average units

def average_units(file: str = "data.csv") -> float:
    rows = load_sales(file)
    if not rows:
        return 0.0
    total_units = sum(row.get("units", 0) for row in rows)
    return round(total_units / len(rows), 2)

# Report line

def report_line(id: int, file: str = "data.csv") -> str:
    row = find_by_id(id, file)
    return f"#{row['id']} {row['name']} ({row['region']}): {row['units']} units, revenue {row_revenue(row):.2f}"
