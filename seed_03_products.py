"""
Tạo CSV: products.csv
Chạy: python seed_03_products.py
"""

import csv
import random

OUTPUT_DIR = "output/Products"

PRODUCTS_DATA = [
    {"name": "Cà Phê Đen", "category": "Cà phê", "price": 29000, "size": "M", "desc": "Cà phê đen truyền thống"},
    {"name": "Cà Phê Sữa", "category": "Cà phê", "price": 35000, "size": "M", "desc": "Cà phê sữa đá"},
    {"name": "Bạc Xỉu", "category": "Cà phê", "price": 35000, "size": "M", "desc": "Bạc xỉu đá mát lạnh"},
    {"name": "Latte", "category": "Cà phê", "price": 49000, "size": "M", "desc": "Latte Ý kinh điển"},
    {"name": "Cappuccino", "category": "Cà phê", "price": 49000, "size": "M", "desc": "Cappuccino bọt sữa mịn"},
    {"name": "Americano", "category": "Cà phê", "price": 39000, "size": "M", "desc": "Americano đậm đà"},
    {"name": "Espresso", "category": "Cà phê", "price": 39000, "size": "S", "desc": "Espresso nguyên chất"},
    {"name": "Caramel Macchiato", "category": "Cà phê", "price": 55000, "size": "M", "desc": "Macchiato caramel thơm ngọt"},
    {"name": "Trà Đào Cam Sả", "category": "Trà", "price": 45000, "size": "L", "desc": "Trà đào cam sả thanh mát"},
    {"name": "Trà Vải", "category": "Trà", "price": 45000, "size": "L", "desc": "Trà vải tươi mát"},
    {"name": "Trà Sen Vàng", "category": "Trà", "price": 42000, "size": "L", "desc": "Trà hạt sen thanh nhẹ"},
    {"name": "Trà Oolong", "category": "Trà", "price": 40000, "size": "M", "desc": "Trà Oolong truyền thống"},
    {"name": "Hồng Trà Sữa", "category": "Trà", "price": 45000, "size": "M", "desc": "Hồng trà sữa béo ngậy"},
    {"name": "Sinh Tố Bơ", "category": "Sinh tố", "price": 49000, "size": "L", "desc": "Sinh tố bơ sáp béo mịn"},
    {"name": "Sinh Tố Xoài", "category": "Sinh tố", "price": 45000, "size": "L", "desc": "Sinh tố xoài tươi"},
    {"name": "Nước Ép Cam", "category": "Nước ép", "price": 39000, "size": "M", "desc": "Nước ép cam tươi 100%"},
    {"name": "Croissant Bơ", "category": "Bánh ngọt", "price": 35000, "size": "", "desc": "Croissant bơ Pháp giòn xốp"},
    {"name": "Bánh Mì Que", "category": "Bánh ngọt", "price": 25000, "size": "", "desc": "Bánh mì que pate"},
    {"name": "Tiramisu", "category": "Bánh ngọt", "price": 55000, "size": "", "desc": "Tiramisu cà phê Ý"},
    {"name": "Cookie Socola", "category": "Bánh ngọt", "price": 30000, "size": "", "desc": "Cookie socola chip"},
]


def generate():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = []
    for i, p in enumerate(PRODUCTS_DATA, start=1):
        rows.append({
            "id": i,
            "name": p["name"],
            "category": p["category"],
            "description": p["desc"],
            "price": p["price"],
            "size": p["size"],
            "is_available": random.random() > 0.1,
            "image_url": "",
        })

    with open(f"{OUTPUT_DIR}/products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ products.csv — {len(rows)} dòng")


if __name__ == "__main__":
    print("=" * 45)
    print("  SEED CSV: PRODUCTS (sản phẩm)")
    print("=" * 45)
    generate()
    print("\n✅ Hoàn tất!")
