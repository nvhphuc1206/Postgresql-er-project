"""
Tạo CSV: customers.csv
Chạy: python seed_04_customers.py
"""

import csv
from utils import random_phone, random_email, random_datetime_recent

OUTPUT_DIR = "output/Customers"

CUSTOMER_NAMES = [
    # Khách hàng thân thiết cao (sẽ được ưu tiên tạo nhiều đơn trong seed_05)
    "Lê Thị Hạnh", "Nguyễn Minh Tuấn", "Trần Văn Đạt", "Phạm Thị Linh", "Hoàng Đức Trí",
    # Khách hàng thường xuyên
    "Ngô Thị Thanh", "Vũ Văn Hùng", "Đỗ Thị Kim", "Bùi Quốc Việt", "Lý Thị Ngân",
    "Trương Minh Đức", "Đặng Thị Tuyết", "Phan Văn Hải", "Huỳnh Thị Oanh", "Dương Văn Tâm",
    "Cao Thị Bảo", "Tô Minh Hiếu", "Lương Thị Phượng", "Hồ Văn Đông", "Mai Thị Cẩm",
    # Khách hàng bình thường
    "Nguyễn Thị Ánh", "Trần Quốc Huy", "Lê Văn Bình", "Phạm Thị Diệu", "Võ Minh Trung",
    "Đinh Thị Giang", "Nguyễn Văn Khoa", "Trần Thị Nhung", "Lê Hoàng Nam", "Phạm Thị Uyên",
    "Châu Văn Khánh", "Lâm Thị Hoa", "Tạ Quang Vinh", "Kiều Thị Thoa", "Mạc Văn Dũng",
    "Nghiêm Thị Lan", "Quách Minh Tân", "Thái Thị Hương", "Ung Văn Phát", "Xa Thị Loan",
    # Khách hàng mới / ít mua
    "Âu Dương Tuấn", "Bạch Thị Nga", "Cù Văn Thắng", "Dư Thị Hồng", "Gia Thị Liên",
    "Hứa Văn Long", "Ích Văn Toàn", "Khương Thị Yến", "Lục Văn Bảo", "Mã Thị Diệu",
    "Nông Văn Hải", "Ông Thị Phúc", "Phó Minh Sơn", "Quản Thị Trang", "Rạng Văn Cường",
    "Sầm Thị Nga", "Tăng Văn Lộc", "Ứng Thị Mai", "Vương Minh Khải", "Xứng Thị Bình",
]


def generate():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    used_phones = set()
    used_emails = set()
    rows = []

    for i, name in enumerate(CUSTOMER_NAMES, start=1):
        phone = random_phone()
        while phone in used_phones:
            phone = random_phone()
        used_phones.add(phone)

        email = random_email(name)
        while email in used_emails:
            email = random_email(name)
        used_emails.add(email)

        rows.append({
            "id": i,
            "full_name": name,
            "phone": phone,
            "email": email,
            "registered_at": random_datetime_recent(days_back=730),
        })

    with open(f"{OUTPUT_DIR}/customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ customers.csv — {len(rows)} dòng")


if __name__ == "__main__":
    print("=" * 45)
    print("  SEED CSV: CUSTOMERS (khách hàng)")
    print("=" * 45)
    generate()
    print("\n✅ Hoàn tất!")
