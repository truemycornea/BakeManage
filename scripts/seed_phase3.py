#!/usr/bin/env python3
"""Seed Phase 3 demo data: lead times, CRM loyalty, stock indent."""

import httpx

BASE = "http://localhost:8000"
H = {"X-Client-Role": "owner", "X-Client-PIN": "sandbox1234"}


def p(path, payload, label):
    r = httpx.post(f"{BASE}{path}", json=payload, headers=H, timeout=10)
    status = "OK" if r.status_code == 200 else f"ERR {r.status_code}"
    print(f"  [{status}] {label}")


print("=== Phase 3: Supplier Lead Times ===")
lead_times = [
    {
        "vendor_name": "Sunrise Mills",
        "ingredient_name": "Chakki Atta (Whole Wheat)",
        "lead_days": 2,
        "last_price_per_unit": 42.0,
    },
    {
        "vendor_name": "Sunrise Mills",
        "ingredient_name": "Maida (Refined Flour)",
        "lead_days": 2,
        "last_price_per_unit": 30.0,
    },
    {
        "vendor_name": "FreshDairy Co.",
        "ingredient_name": "Amul Butter (Unsalted)",
        "lead_days": 1,
        "last_price_per_unit": 510.0,
    },
    {
        "vendor_name": "FreshDairy Co.",
        "ingredient_name": "Full Cream Milk (Amul)",
        "lead_days": 1,
        "last_price_per_unit": 62.0,
    },
    {
        "vendor_name": "GrowGreen Farms",
        "ingredient_name": "Full Cream Milk (Amul)",
        "lead_days": 2,
        "last_price_per_unit": 58.0,
    },
    {
        "vendor_name": "ChocWorld Imports",
        "ingredient_name": "Dark Chocolate Chips",
        "lead_days": 6,
        "last_price_per_unit": 550.0,
    },
    {
        "vendor_name": "Bakery Wholesale",
        "ingredient_name": "Active Dry Yeast",
        "lead_days": 3,
        "last_price_per_unit": 680.0,
    },
    {
        "vendor_name": "Bakery Wholesale",
        "ingredient_name": "Baking Powder (Weikfield)",
        "lead_days": 3,
        "last_price_per_unit": 280.0,
    },
    {
        "vendor_name": "SpiceHaven",
        "ingredient_name": "Cardamom Powder",
        "lead_days": 5,
        "last_price_per_unit": 2800.0,
    },
    {
        "vendor_name": "SpiceHaven",
        "ingredient_name": "Vanilla Extract",
        "lead_days": 4,
        "last_price_per_unit": 850.0,
    },
    {
        "vendor_name": "PackPro India",
        "ingredient_name": "Cake Boxes (6-inch)",
        "lead_days": 2,
        "last_price_per_unit": 18.0,
    },
]
for lt in lead_times:
    p("/supply-chain/lead-times", lt, f"{lt['vendor_name']} -> {lt['ingredient_name']}")

print("=== Phase 3: CRM Loyalty Records ===")
loyalty = [
    {
        "customer_name": "Aarav Mehta",
        "phone": "+919876540001",
        "birthday": "1992-04-10",
        "total_purchases": 34,
        "total_spend_inr": 8200.0,
    },
    {
        "customer_name": "Divya Krishnan",
        "phone": "+919876540002",
        "birthday": "1988-12-25",
        "total_purchases": 22,
        "total_spend_inr": 4750.0,
    },
    {
        "customer_name": "Raj Kapoor",
        "phone": "+919876540003",
        "birthday": "1975-07-04",
        "total_purchases": 56,
        "total_spend_inr": 14600.0,
    },
    {
        "customer_name": "Sneha Patel",
        "phone": "+919876540004",
        "birthday": "1995-02-14",
        "total_purchases": 12,
        "total_spend_inr": 2300.0,
    },
    {
        "customer_name": "Vikram Nair",
        "phone": "+919876540005",
        "birthday": "1983-09-30",
        "total_purchases": 8,
        "total_spend_inr": 1400.0,
    },
    {
        "customer_name": "Anand Iyer",
        "phone": "+919876540007",
        "birthday": "1980-11-08",
        "total_purchases": 30,
        "total_spend_inr": 7400.0,
    },
    {
        "customer_name": "Meena Bansal",
        "phone": "+919876540008",
        "birthday": "1998-03-21",
        "total_purchases": 6,
        "total_spend_inr": 900.0,
    },
    {
        "customer_name": "Kabir Singh",
        "phone": "+919876540009",
        "birthday": "1987-08-17",
        "total_purchases": 18,
        "total_spend_inr": 3800.0,
    },
    {
        "customer_name": "Riya Verma",
        "phone": "+919876540010",
        "birthday": "1993-01-03",
        "total_purchases": 25,
        "total_spend_inr": 5900.0,
    },
]
for cust in loyalty:
    p("/crm/loyalty/upsert", cust, cust["customer_name"])

print("=== Phase 3: Supply Chain Indent ===")
p(
    "/supply-chain/indent",
    {"threshold_kg": 50.0, "vendor_name": "Sunrise Mills"},
    "Auto-indent low-stock",
)

print("=== Platform State ===")
r = httpx.get(f"{BASE}/dashboard/summary", headers=H, timeout=10)
d = r.json()
print(f"  Stock items       : {d.get('stock_items', '?')}")
print(f"  Quality checks    : {d.get('quality_inspections', '?')}")
print(f"  Proofing readings : {d.get('proofing_readings', '?')}")

r2 = httpx.get(f"{BASE}/crm/loyalty", headers=H, timeout=10)
if r2.status_code == 200:
    customers = r2.json().get("all_customers", [])
    tiers = r2.json().get("tier_breakdown", {})
    print(f"  Loyalty customers : {len(customers)}")
    for tier, count in tiers.items():
        print(f"    {tier}: {count}")

r3 = httpx.get(f"{BASE}/supply-chain/lead-times", headers=H, timeout=10)
if r3.status_code == 200:
    print(f"  Lead-time records : {len(r3.json().get('lead_times', []))}")

print("Seed complete -- platform ready for UAT")
