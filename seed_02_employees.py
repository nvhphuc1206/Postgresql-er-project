"""
Tạo CSV: employees.csv + fulltime_employees.csv + parttime_employees.csv
Chạy: python seed_02_employees.py
"""

import csv
import random
from datetime import timedelta, datetime
from utils import random_phone, random_email, random_date

OUTPUT_DIR = "output/Employees"

EMPLOYEE_NAMES = [
    "Nguyễn Văn An", "Trần Thị Bích", "Lê Hoàng Cường", "Phạm Thị Dung",
    "Hoàng Văn Em", "Ngô Thị Phương", "Đỗ Minh Quân", "Vũ Thị Hoa",
    "Bùi Thanh Tùng", "Lý Thị Mai", "Trương Văn Khải", "Đặng Thị Lan",
    "Phan Văn Minh", "Huỳnh Thị Ngọc", "Dương Văn Phúc", "Cao Thị Quỳnh",
    "Tô Văn Sơn", "Lương Thị Thảo", "Hồ Văn Uy", "Mai Thị Vân",
    "Nguyễn Đức Anh", "Trần Minh Châu", "Lê Thị Diễm", "Phạm Quốc Bảo",
    "Võ Thị Hằng", "Đinh Văn Lợi", "Nguyễn Thị Mỹ", "Trần Văn Nghĩa",
    "Lê Phước Thiện", "Phạm Thị Yến",
]

ROLES = ["manager", "barista", "cashier", "shipper"]
NUM_BRANCHES = 6  # Phải khớp với seed_01


def generate():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    branch_ids = list(range(1, NUM_BRANCHES + 1))
    used_phones = set()
    used_emails = set()

    # --- employees.csv ---
    emp_rows = []
    for i, name in enumerate(EMPLOYEE_NAMES, start=1):
        phone = random_phone()
        while phone in used_phones:
            phone = random_phone()
        used_phones.add(phone)

        email = random_email(name)
        while email in used_emails:
            email = random_email(name)
        used_emails.add(email)

        role = random.choice(ROLES)
        emp_type = "fulltime" if role == "manager" else random.choice(["fulltime", "parttime"])

        emp_rows.append({
            "id": i,
            "branch_id": random.choice(branch_ids),
            "full_name": name,
            "phone": phone,
            "email": email,
            "role": role,
            "employee_type": emp_type,
            "hire_date": random_date(2020, 2025),
            "is_active": True,
        })

    with open(f"{OUTPUT_DIR}/employees.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=emp_rows[0].keys())
        writer.writeheader()
        writer.writerows(emp_rows)
    print(f"  ✓ employees.csv — {len(emp_rows)} dòng")

    # --- fulltime_employees.csv ---
    ft_rows = []
    ft_id = 1
    for emp in emp_rows:
        if emp["employee_type"] != "fulltime":
            continue

        if emp["role"] == "manager":
            salary = random.randint(12000000, 18000000)
            allowance = random.choice([1000000, 1500000, 2000000])
        elif emp["role"] == "barista":
            salary = random.randint(7000000, 10000000)
            allowance = random.choice([500000, 700000])
        else:
            salary = random.randint(6000000, 9000000)
            allowance = random.choice([300000, 500000])

        contract_start = emp["hire_date"]
        if random.random() < 0.7:
            start_dt = datetime.strptime(contract_start, "%Y-%m-%d")
            contract_end = (start_dt + timedelta(days=random.choice([365, 730, 1095]))).strftime("%Y-%m-%d")
        else:
            contract_end = ""

        ft_rows.append({
            "id": ft_id,
            "employee_id": emp["id"],
            "monthly_salary": salary,
            "annual_leave_days": 12,
            "health_insurance": True,
            "social_insurance": True,
            "contract_start": contract_start,
            "contract_end": contract_end,
            "allowance": allowance,
        })
        ft_id += 1

    with open(f"{OUTPUT_DIR}/fulltime_employees.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ft_rows[0].keys())
        writer.writeheader()
        writer.writerows(ft_rows)
    print(f"  ✓ fulltime_employees.csv — {len(ft_rows)} dòng")

    # --- parttime_employees.csv ---
    pt_rows = []
    pt_id = 1
    days_options = ["Mon,Wed,Fri", "Tue,Thu,Sat", "Mon,Tue,Wed", "Thu,Fri,Sat,Sun", "Sat,Sun"]
    shifts = ["morning", "afternoon", "evening"]

    for emp in emp_rows:
        if emp["employee_type"] != "parttime":
            continue

        pt_rows.append({
            "id": pt_id,
            "employee_id": emp["id"],
            "hourly_rate": random.choice([25000, 28000, 30000, 32000, 35000]),
            "max_hours_per_week": random.choice([20, 24, 28]),
            "min_hours_per_week": random.choice([8, 12]),
            "overtime_rate": 1.5,
            "available_days": random.choice(days_options),
            "preferred_shift": random.choice(shifts),
        })
        pt_id += 1

    with open(f"{OUTPUT_DIR}/parttime_employees.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=pt_rows[0].keys())
        writer.writeheader()
        writer.writerows(pt_rows)
    print(f"  ✓ parttime_employees.csv — {len(pt_rows)} dòng")


if __name__ == "__main__":
    print("=" * 45)
    print("  SEED CSV: EMPLOYEES (nhân viên)")
    print("=" * 45)
    generate()
    print("\n✅ Hoàn tất!")
