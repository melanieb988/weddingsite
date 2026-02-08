import os
import csv
import psycopg2

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise Exception("DATABASE_URL not set!")

# Connect to the database
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
# cur.execute("""DELETE FROM guests a
# USING guests b
# WHERE a.ctid > b.ctid
#   AND a.name = b.name
#   AND a.household_id = b.household_id;""")
conn.commit()
# with open("guest_db.csv", newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     for row in reader:
#         cur.execute("""
#             INSERT INTO guests (name, household_id, plus_one_allowed, attending, meal_choice, plus_one_name, song_rec)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (guest_id) DO NOTHING
#         """, (
#             row.get("name"),
#             row.get("household_id"),
#             row.get("plus_one_allowed", "FALSE") == "TRUE",
#             row.get("attending") or None,
#             row.get("meal_choice") or None,
#             row.get("plus_one_name") or None,
#             row.get("song_rec") or None
#         ))

# conn.commit()
import os
import csv
import psycopg2

# =========================
# CONFIG
# =========================
DB_URL = os.environ.get("DATABASE_URL")
CSV_FILE = "/Users/melaniebowden/Downloads/guest_db 1.csv"  # Path to your CSV

if not DB_URL:
    raise Exception("DATABASE_URL not set!")

# =========================
# CONNECT TO DATABASE
# =========================
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
# <-- replace with your CSV path

TABLE_COLUMNS = [
    "name",
    "household_id",
    "plus_one_allowed",
    "attending",
    "meal_choice",
    "plus_one_name",
    "song_rec",
    "dietary_restriction"
]

if not DB_URL:
    raise Exception("DATABASE_URL not set!")

# =========================
# CONNECT TO DATABASE
# =========================
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

try:
    # -------------------------
    # DELETE EXISTING DATA
    # -------------------------
    print("Deleting existing rows from guests table...")
    cur.execute("DELETE FROM guests;")
    conn.commit()
    print("Existing data deleted.")

    # -------------------------
    # LOAD CSV DATA
    # -------------------------
    print(f"Loading new data from {CSV_FILE}...")
    with open(CSV_FILE, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        rows_inserted = 0
        for row in reader:
            # Keep only columns that exist in SQL table
            filtered_row = {k: row[k] for k in TABLE_COLUMNS if k in row}

            # Skip rows with empty name (NOT NULL)
            name = filtered_row.get("name", "").strip()
            if not name:
                print(f"Skipping row with empty name: {row}")
                continue

            plus_one_allowed = filtered_row.get("plus_one_allowed", "").strip().upper() == "TRUE"

            cur.execute("""
                INSERT INTO guests (
                    name,
                    household_id,
                    plus_one_allowed,
                    attending,
                    meal_choice,
                    plus_one_name,
                    song_rec,
                    dietary_restriction
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name,
                filtered_row.get("household_id") or None,
                plus_one_allowed,
                filtered_row.get("attending") or None,
                filtered_row.get("meal_choice") or None,
                filtered_row.get("plus_one_name") or None,
                filtered_row.get("song_rec") or None,
                filtered_row.get("dietary_restriction") or None
            ))
            rows_inserted += 1

    conn.commit()
    print(f"CSV data loaded successfully! {rows_inserted} rows inserted.")

except Exception as e:
    conn.rollback()
    print("Error:", e)

finally:
    cur.close()
    conn.close()
    print("Database connection closed.")

