"""
Tạo CSV: branches.csv + dine_in_branches.csv + delivery_branches.csv
Chạy: python seed_01_branches.py
"""

import csv
import random

OUTPUT_DIR = "output/Branches"

BRANCH_DATA = [
    {"code": "CN01", "address": "12 Nguyễn Huệ, Quận 1, TP.HCM", "phone": "028-1234-5601", "type": "dine_in"},
    {"code": "CN02", "address": "45 Lê Lợi, Quận 1, TP.HCM", "phone": "028-1234-5602", "type": "dine_in"},
    {"code": "CN03", "address": "78 Cách Mạng Tháng 8, Quận 3, TP.HCM", "phone": "028-1234-5603", "type": "hybrid"},
    {"code": "CN04", "address": "234 Nguyễn Văn Cừ, Quận 5, TP.HCM", "phone": "028-1234-5604", "type": "delivery"},
    {"code": "CN05", "address": "56 Phan Xích Long, Phú Nhuận, TP.HCM", "phone": "028-1234-5605", "type": "dine_in"},
    {"code": "CN06", "address": "189 Võ Văn Ngân, Thủ Đức, TP.HCM", "phone": "028-1234-5606", "type": "delivery"},
]


def generate():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- branches.csv ---
    branches_rows = []
    for i, b in enumerate(BRANCH_DATA, start=1):
        branches_rows.append({
            "id": i,
            "branch_code": b["code"],
            "address": b["address"],
            "phone": b["phone"],
            "branch_type": b["type"],
            "opening_time": "07:00",
            "closing_time": "22:00",
            "is_active": True,
        })

    with open(f"{OUTPUT_DIR}/branches.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=branches_rows[0].keys())
        writer.writeheader()
        writer.writerows(branches_rows)
    print(f"  ✓ branches.csv — {len(branches_rows)} dòng")

    # --- dine_in_branches.csv ---
    dine_in_rows = []
    dine_id = 1
    for b in branches_rows:
        if b["branch_type"] in ("dine_in", "hybrid"):
            tables = random.randint(10, 30)
            chairs = tables * random.choice([2, 4])
            dine_in_rows.append({
                "id": dine_id,
                "branch_id": b["id"],
                "seating_capacity": chairs,
                "number_of_tables": tables,
                "number_of_chairs": chairs,
                "has_parking": random.choice([True, False]),
                "service_charge_percent": random.choice([0, 0, 5, 10]),
                "has_wifi": True,
            })
            dine_id += 1

    with open(f"{OUTPUT_DIR}/dine_in_branches.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dine_in_rows[0].keys())
        writer.writeheader()
        writer.writerows(dine_in_rows)
    print(f"  ✓ dine_in_branches.csv — {len(dine_in_rows)} dòng")

    # --- delivery_branches.csv ---
    delivery_rows = []
    del_id = 1
    for b in branches_rows:
        if b["branch_type"] in ("delivery", "hybrid"):
            delivery_rows.append({
                "id": del_id,
                "branch_id": b["id"],
                "delivery_radius_km": random.choice([3.0, 5.0, 7.0, 10.0]),
                "base_delivery_fee": random.choice([15000, 20000, 25000]),
                "free_delivery_min": random.choice([100000, 150000, 200000, ""]),
                "max_concurrent_orders": random.randint(15, 30),
                "partner_apps": random.choice(["GrabFood, ShopeeFood", "GrabFood", "ShopeeFood, GoFood"]),
            })
            del_id += 1

    with open(f"{OUTPUT_DIR}/delivery_branches.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=delivery_rows[0].keys())
        writer.writeheader()
        writer.writerows(delivery_rows)
    print(f"  ✓ delivery_branches.csv — {len(delivery_rows)} dòng")


if __name__ == "__main__":
    print("=" * 45)
    print("  SEED CSV: BRANCHES (chi nhánh)")
    print("=" * 45)
    generate()
    print("\n✅ Hoàn tất!")
