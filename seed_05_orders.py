"""
Tạo CSV: orders.csv + order_items.csv
Chạy: python seed_05_orders.py

Chiến lược phân bổ dữ liệu:
  - 600 đơn lịch sử: 2024-01-01 → 2025-12-31  (trải đều 2 năm)
  - 200 đơn gần đây: 2025-12-18 → 2026-03-18  (90 ngày gần nhất cho sp_customer_analysis)
  - Khách VIP (id 1-5): xuất hiện nhiều ở đơn gần đây → đủ điều kiện phân loại VIP
"""

import csv
import random
from datetime import datetime, timedelta

OUTPUT_DIR = "output/Orders"

NUM_BRANCHES   = 6
NUM_EMPLOYEES  = 30
NUM_CUSTOMERS  = 60   # Khớp với seed_04
NUM_PRODUCTS   = 20

# ID khách hàng thân thiết cao — sẽ được ưu tiên trong đơn gần đây
VIP_CUSTOMER_IDS = [1, 2, 3, 4, 5]

ORDER_NOTES = [
    "Ít đường", "Nhiều đá", "Không đá", "Thêm shot", "Ít đá",
    "Đường nhiều", "Thêm kem", "Nóng", "Đá xay", "", "", "",
]

PAYMENT_METHODS = ["cash", "card", "momo", "bank_transfer"]

# Order types hợp lệ theo loại chi nhánh (khớp với seed_01)
# CN01=dine_in, CN02=dine_in, CN03=hybrid, CN04=delivery, CN05=dine_in, CN06=delivery
BRANCH_ORDER_TYPES = {
    1: ["dine_in", "dine_in", "takeaway"],            # CN01 — dine_in
    2: ["dine_in", "dine_in", "takeaway"],            # CN02 — dine_in
    3: ["dine_in", "takeaway", "delivery"],           # CN03 — hybrid
    4: ["delivery", "delivery", "takeaway"],          # CN04 — delivery
    5: ["dine_in", "dine_in", "takeaway"],            # CN05 — dine_in
    6: ["delivery", "delivery", "takeaway"],          # CN06 — delivery
}

# Tỷ lệ trạng thái: 70% completed để có đủ dữ liệu thống kê
ORDER_STATUSES = (
    ["completed"] * 7
    + ["preparing"] * 1
    + ["pending"] * 1
    + ["cancelled"] * 1
)

DELIVERY_ADDRESSES = [
    "100 Điện Biên Phủ, Quận Bình Thạnh, TP.HCM",
    "55 Lý Thường Kiệt, Quận 10, TP.HCM",
    "23 Trần Hưng Đạo, Quận 1, TP.HCM",
    "88 Nguyễn Thị Minh Khai, Quận 3, TP.HCM",
    "67 Hai Bà Trưng, Quận 1, TP.HCM",
    "142 Cộng Hòa, Tân Bình, TP.HCM",
    "300 Nguyễn Văn Linh, Quận 7, TP.HCM",
    "15 Pasteur, Quận 3, TP.HCM",
    "210 Lê Văn Sỹ, Quận 3, TP.HCM",
    "77 Nguyễn Đình Chiểu, Quận 1, TP.HCM",
]

# Giá sản phẩm (khớp với seed_03)
PRODUCT_PRICES = {
    1: 29000,  2: 35000,  3: 35000,  4: 49000,  5: 49000,
    6: 39000,  7: 39000,  8: 55000,  9: 45000, 10: 45000,
   11: 42000, 12: 40000, 13: 45000, 14: 49000, 15: 45000,
   16: 39000, 17: 35000, 18: 25000, 19: 55000, 20: 30000,
}

# Phân bổ phương thức thanh toán theo chi nhánh (thực tế hơn)
BRANCH_PAYMENT_WEIGHTS = {
    1: {"cash": 4, "card": 3, "momo": 2, "bank_transfer": 1},   # Q1 — đa dạng
    2: {"cash": 3, "card": 4, "momo": 2, "bank_transfer": 1},   # Q1 — card nhiều
    3: {"cash": 2, "card": 2, "momo": 4, "bank_transfer": 2},   # Q3 — momo nhiều
    4: {"cash": 1, "card": 2, "momo": 3, "bank_transfer": 4},   # Q5 — bank_transfer nhiều
    5: {"cash": 3, "card": 2, "momo": 3, "bank_transfer": 2},   # Phú Nhuận — cân bằng
    6: {"cash": 2, "card": 1, "momo": 4, "bank_transfer": 3},   # Thủ Đức — momo + bank
}


def weighted_payment(branch_id):
    w = BRANCH_PAYMENT_WEIGHTS.get(branch_id, {"cash": 1, "card": 1, "momo": 1, "bank_transfer": 1})
    methods = list(w.keys())
    weights = list(w.values())
    return random.choices(methods, weights=weights, k=1)[0]


def random_dt_between(start: datetime, end: datetime) -> str:
    delta_seconds = int((end - start).total_seconds())
    offset = timedelta(seconds=random.randint(0, delta_seconds))
    dt = start + offset
    dt = dt.replace(hour=random.randint(7, 21), minute=random.randint(0, 59), second=0)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def make_order(order_id, date_start, date_end, customer_pool=None):
    """Tạo 1 đơn hàng trong khoảng thời gian cho trước."""
    branch_id   = random.randint(1, NUM_BRANCHES)
    employee_id = random.randint(1, NUM_EMPLOYEES)

    if customer_pool:
        # Dùng pool có trọng số để tạo khách VIP
        customer_id = random.choice(customer_pool)
    else:
        customer_id = random.randint(1, NUM_CUSTOMERS) if random.random() < 0.65 else ""

    order_type     = random.choice(BRANCH_ORDER_TYPES[branch_id])
    order_date     = random_dt_between(date_start, date_end)
    payment_method = weighted_payment(branch_id)
    status         = random.choice(ORDER_STATUSES)

    delivery_fee     = 0
    delivery_address = ""
    service_charge   = 0

    if order_type == "delivery":
        delivery_fee     = random.choice([0, 15000, 20000, 25000])
        delivery_address = random.choice(DELIVERY_ADDRESSES)
    elif order_type == "dine_in":
        service_charge = random.choice([0, 0, 0, 5000, 10000])

    # 1–5 items, khách VIP thường mua nhiều hơn
    max_items = 5 if customer_id not in VIP_CUSTOMER_IDS else random.choice([3, 4, 5])
    num_items = random.randint(1, max_items)
    selected  = random.sample(list(PRODUCT_PRICES.keys()), min(num_items, len(PRODUCT_PRICES)))

    items      = []
    order_total = 0
    for prod_id in selected:
        qty        = random.randint(1, 3)
        unit_price = PRODUCT_PRICES[prod_id]
        note       = random.choice(ORDER_NOTES)
        items.append({
            "order_id":   order_id,
            "product_id": prod_id,
            "quantity":   qty,
            "unit_price": unit_price,
            "note":       note,
        })
        order_total += unit_price * qty

    final_total = order_total + delivery_fee + service_charge

    order = {
        "id":               order_id,
        "branch_id":        branch_id,
        "customer_id":      customer_id,
        "employee_id":      employee_id,
        "order_type":       order_type,
        "order_date":       order_date,
        "total_amount":     final_total,
        "delivery_fee":     delivery_fee,
        "service_charge":   service_charge,
        "payment_method":   payment_method,
        "status":           status,
        "delivery_address": delivery_address,
    }
    return order, items


def generate():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    order_rows = []
    item_rows  = []
    item_id    = 1
    order_id   = 1

    # ── Giai đoạn 1: đơn lịch sử 2024–2025 (600 đơn) ──────────────────────
    hist_start = datetime(2024, 1, 1)
    hist_end   = datetime(2025, 12, 31)

    for _ in range(600):
        order, items = make_order(order_id, hist_start, hist_end)
        order_rows.append(order)
        for it in items:
            it["id"] = item_id
            item_rows.append(it)
            item_id += 1
        order_id += 1

    # ── Giai đoạn 2: đơn gần đây 90 ngày (200 đơn) ─────────────────────────
    # Pool khách: VIP xuất hiện ~40%, khách thường ~45%, vãng lai ~15%
    recent_customer_pool = (
        VIP_CUSTOMER_IDS * 8                               # VIP — xuất hiện nhiều
        + list(range(6, NUM_CUSTOMERS + 1)) * 1            # Khách thường
        + [""] * 4                                         # Vãng lai
    )

    recent_start = datetime(2025, 12, 18)
    recent_end   = datetime(2026, 3, 18)

    for _ in range(200):
        order, items = make_order(order_id, recent_start, recent_end,
                                  customer_pool=recent_customer_pool)
        order_rows.append(order)
        for it in items:
            it["id"] = item_id
            item_rows.append(it)
            item_id += 1
        order_id += 1

    # ── Ghi CSV ─────────────────────────────────────────────────────────────
    with open(f"{OUTPUT_DIR}/orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=order_rows[0].keys())
        writer.writeheader()
        writer.writerows(order_rows)
    print(f"  ✓ orders.csv — {len(order_rows)} dòng")

    with open(f"{OUTPUT_DIR}/order_items.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=item_rows[0].keys())
        writer.writeheader()
        writer.writerows(item_rows)
    print(f"  ✓ order_items.csv — {len(item_rows)} dòng")


if __name__ == "__main__":
    print("=" * 45)
    print("  SEED CSV: ORDERS & ORDER_ITEMS (đơn hàng)")
    print("=" * 45)
    generate()
    print("\n✅ Hoàn tất!")
