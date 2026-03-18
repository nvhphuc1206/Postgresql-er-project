"""
============================================
IMPORT CSV VÀO DATABASE
============================================
Script đọc file samplesheet.csv để biết bảng nào
cần import và file CSV nằm ở đâu.

Cài đặt:
  pip install psycopg2-binary python-dotenv

Tạo file .env:
  DATABASE_URL=postgresql://neondb_owner:xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require

File samplesheet.csv có format:
  table,filepath
  branches,./output/branches.csv
  employees,./output/employees.csv

Cách dùng:
  python import_csv.py --input samplesheet.csv             Import theo samplesheet
  python import_csv.py --input samplesheet.csv --dry-run   Chạy thử, không ghi vào DB
  python import_csv.py --input samplesheet.csv --no-clear  Giữ dữ liệu cũ
  python import_csv.py --list                              Xem danh sách bảng hỗ trợ
  python import_csv.py --sample                            Tạo file samplesheet mẫu
============================================
"""

import os
import sys
import csv
import argparse
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ============================================
# THỨ TỰ IMPORT (quan trọng vì Foreign Key)
# ============================================
IMPORT_ORDER = [
    "branches",
    "dine_in_branches",
    "delivery_branches",
    "employees",
    "fulltime_employees",
    "parttime_employees",
    "products",
    "customers",
    "orders",
    "order_items",
]

# ============================================
# CỘT CỦA TỪNG BẢNG (khớp với header CSV)
# ============================================
TABLE_COLUMNS = {
    "branches": [
        "branch_code", "address", "phone", "branch_type",
        "opening_time", "closing_time", "is_active",
    ],
    "dine_in_branches": [
        "branch_id", "seating_capacity", "number_of_tables",
        "number_of_chairs", "has_parking", "service_charge_percent", "has_wifi",
    ],
    "delivery_branches": [
        "branch_id", "delivery_radius_km", "base_delivery_fee",
        "free_delivery_min", "max_concurrent_orders", "partner_apps",
    ],
    "employees": [
        "branch_id", "full_name", "phone", "email",
        "role", "employee_type", "hire_date", "is_active",
    ],
    "fulltime_employees": [
        "employee_id", "monthly_salary", "annual_leave_days",
        "health_insurance", "social_insurance",
        "contract_start", "contract_end", "allowance",
    ],
    "parttime_employees": [
        "employee_id", "hourly_rate", "max_hours_per_week",
        "min_hours_per_week", "overtime_rate", "available_days", "preferred_shift",
    ],
    "products": [
        "name", "category", "description", "price",
        "size", "is_available", "image_url",
    ],
    "customers": [
        "full_name", "phone", "email", "registered_at",
    ],
    "orders": [
        "branch_id", "customer_id", "employee_id", "order_type",
        "order_date", "total_amount", "delivery_fee", "service_charge",
        "payment_method", "status", "delivery_address",
    ],
    "order_items": [
        "order_id", "product_id", "quantity", "unit_price", "note",
    ],
}


# ============================================
# HÀM XỬ LÝ GIÁ TRỊ
# ============================================
def clean_value(value):
    """Ô trống trong CSV → NULL trong database"""
    if value == "" or value is None:
        return None
    return value


# ============================================
# ARGPARSE
# ============================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Import file CSV vào database PostgreSQL (Neon)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
File samplesheet.csv có format (2 cột, có header):
  table,filepath
  branches,./output/branches.csv
  dine_in_branches,./output/dine_in_branches.csv
  employees,./output/employees.csv

Ví dụ sử dụng:
  python import_csv.py --input samplesheet.csv             Import theo samplesheet
  python import_csv.py --input samplesheet.csv --dry-run   Chạy thử
  python import_csv.py --input samplesheet.csv --no-clear  Không xóa dữ liệu cũ
  python import_csv.py --list                              Xem bảng hỗ trợ
  python import_csv.py --sample                            Tạo samplesheet mẫu
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input", "-i",
        metavar="SAMPLESHEET",
        help="Đường dẫn đến file samplesheet.csv",
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="Xem danh sách tất cả bảng hỗ trợ",
    )
    group.add_argument(
        "--sample", "-s",
        action="store_true",
        help="Tạo file samplesheet_example.csv mẫu",
    )

    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="KHÔNG xóa dữ liệu cũ trước khi import",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chạy thử: đọc CSV và đếm nhưng KHÔNG ghi vào database",
    )

    return parser.parse_args()


# ============================================
# ĐỌC SAMPLESHEET
# ============================================
def read_samplesheet(samplesheet_path):
    """
    Đọc samplesheet.csv → danh sách (table, filepath)
    đã sắp xếp theo thứ tự Foreign Key.
    """

    if not os.path.exists(samplesheet_path):
        print(f"❌ Không tìm thấy file: {samplesheet_path}")
        sys.exit(1)

    entries = []
    with open(samplesheet_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None or "table" not in reader.fieldnames or "filepath" not in reader.fieldnames:
            print("❌ Samplesheet phải có header: table,filepath")
            print("   Ví dụ:")
            print("     table,filepath")
            print("     branches,./output/branches.csv")
            sys.exit(1)

        for line_num, row in enumerate(reader, start=2):
            table = row["table"].strip()
            filepath = row["filepath"].strip()

            # Chuẩn hóa đường dẫn (Windows \ → /)
            filepath = os.path.normpath(filepath)

            if table not in TABLE_COLUMNS:
                print(f"⚠️  Dòng {line_num}: bảng '{table}' không hợp lệ — bỏ qua")
                continue

            if not os.path.exists(filepath):
                print(f"⚠️  Dòng {line_num}: không tìm thấy file '{filepath}' — bỏ qua")
                continue

            entries.append((table, filepath))

    if not entries:
        print("❌ Không có dòng hợp lệ nào trong samplesheet!")
        sys.exit(1)

    # Sắp xếp theo thứ tự Foreign Key
    order_index = {table: i for i, table in enumerate(IMPORT_ORDER)}
    entries.sort(key=lambda x: order_index.get(x[0], 999))

    return entries


# ============================================
# IMPORT 1 BẢNG
# ============================================
def import_table(cur, table_name, csv_path, no_clear=False, dry_run=False):
    """Import 1 file CSV vào 1 bảng"""

    if table_name not in TABLE_COLUMNS:
        print(f"  ⚠️  Không biết cấu trúc bảng {table_name} — bỏ qua")
        return 0

    columns = TABLE_COLUMNS[table_name]

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"  ⚠️  {csv_path} trống — bỏ qua")
        return 0

    if dry_run:
        print(f"  🔍 {table_name} ← {csv_path} — {len(rows)} dòng (dry-run)")
        return len(rows)

    if not no_clear:
        cur.execute(f"DELETE FROM {table_name}")
        cur.execute(f"ALTER SEQUENCE IF EXISTS {table_name}_id_seq RESTART WITH 1")

    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

    count = 0
    for row in rows:
        values = [clean_value(row.get(col, "")) for col in columns]
        cur.execute(sql, values)
        count += 1

    print(f"  ✓ {table_name} ← {csv_path} — {count} dòng")
    return count


# ============================================
# HIỂN THỊ DANH SÁCH BẢNG
# ============================================
def show_list():
    print("=" * 55)
    print("  DANH SÁCH BẢNG HỖ TRỢ")
    print("=" * 55)
    print(f"\n  {'Bảng':<25} {'Số cột':<10} {'Cột'}")
    print(f"  {'─' * 25} {'─' * 10} {'─' * 40}")
    for table in IMPORT_ORDER:
        cols = TABLE_COLUMNS[table]
        print(f"  {table:<25} {len(cols):<10} {', '.join(cols[:4])}...")
    print(f"\n  Tổng: {len(IMPORT_ORDER)} bảng")
    print(f"\n  Thứ tự FK: {' → '.join(IMPORT_ORDER)}")


# ============================================
# TẠO SAMPLESHEET MẪU
# ============================================
def create_sample():
    filename = "samplesheet_example.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table", "filepath"])
        for table in IMPORT_ORDER:
            writer.writerow([table, f"./output/{table}.csv"])

    print(f"✅ Đã tạo file mẫu: {filename}")
    print(f"\nNội dung:")
    with open(filename, "r") as f:
        print(f.read())
    print("Chỉnh sửa filepath cho đúng rồi chạy:")
    print(f"  python import_csv.py --input {filename}")


# ============================================
# HÀM CHÍNH
# ============================================
def main():
    args = parse_args()

    if args.list:
        show_list()
        return

    if args.sample:
        create_sample()
        return

    print("=" * 55)
    if args.dry_run:
        print("  IMPORT CSV → DATABASE (DRY RUN)")
    else:
        print("  IMPORT CSV → DATABASE")
    print("=" * 55)

    if not DATABASE_URL:
        print("\n❌ Không tìm thấy DATABASE_URL!")
        print("Tạo file .env với nội dung:")
        print('DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require')
        return

    print(f"\n📄 Đọc samplesheet: {args.input}")
    entries = read_samplesheet(args.input)

    print(f"📋 Tìm thấy {len(entries)} bảng cần import:")
    for table, filepath in entries:
        print(f"   {table:<25} ← {filepath}")

    if args.no_clear:
        print("\n🔒 Giữ dữ liệu cũ (--no-clear)")
    if args.dry_run:
        print("🔍 Chế độ dry-run — không ghi vào database")

    print(f"\n🔗 Đang kết nối...")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cur = conn.cursor()
        print("✓ Kết nối thành công!\n")

        total = 0

        # Xóa dữ liệu cũ theo thứ tự NGƯỢC Foreign Key
        # (bảng con xóa trước, bảng cha xóa sau)
        if not args.no_clear and not args.dry_run:
            tables_to_clear = [t for t, _ in entries]
            # Sắp xếp ngược: bảng phụ thuộc xóa trước
            reverse_order = list(reversed(IMPORT_ORDER))
            tables_to_clear.sort(key=lambda x: reverse_order.index(x) if x in reverse_order else 999)

            print("🗑️  Xóa dữ liệu cũ (thứ tự ngược FK):")
            for table in tables_to_clear:
                cur.execute(f"DELETE FROM {table}")
                cur.execute(f"ALTER SEQUENCE IF EXISTS {table}_id_seq RESTART WITH 1")
                print(f"   ✓ {table}")
            print()

        for table, filepath in entries:
            count = import_table(cur, table, filepath, no_clear=True, dry_run=args.dry_run)
            total += count

        if args.dry_run:
            conn.rollback()
        else:
            conn.commit()

        print("\n" + "=" * 55)
        print(f"  ✅ HOÀN TẤT — {total} dòng {'đã đọc' if args.dry_run else 'đã import'}")
        print("=" * 55)

        if not args.dry_run:
            print("\n📊 Kiểm tra trong database:")
            for table, _ in entries:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                db_count = cur.fetchone()[0]
                print(f"  {table:.<35} {db_count:>6} dòng")

    except psycopg2.Error as e:
        print(f"\n❌ Lỗi database: {e}")
        if conn:
            conn.rollback()
            print("↩️  Đã rollback.")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("🔌 Đã đóng kết nối.")


if __name__ == "__main__":
    main()