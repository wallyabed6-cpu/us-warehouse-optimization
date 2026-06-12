"""Load uscities.csv into SQLite and run the three SQL query files."""
import csv
import sqlite3
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(ROOT, "data", "warehouse.db")
CSV_PATH = os.path.join(ROOT, "data", "uscities.csv")
SQL_DIR = os.path.join(ROOT, "sql")

KEEP_COLS = {"city", "state_id", "state_name", "lat", "lng", "population"}


def load_csv(conn):
    conn.execute("DROP TABLE IF EXISTS cities")
    conn.execute("""
        CREATE TABLE cities (
            city       TEXT,
            state_id   TEXT,
            state_name TEXT,
            lat        REAL,
            lng        REAL,
            population INTEGER
        )
    """)
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            try:
                pop = int(float(row["population"])) if row["population"] else 0
            except ValueError:
                pop = 0
            rows.append((
                row["city"],
                row["state_id"],
                row["state_name"],
                float(row["lat"]) if row["lat"] else None,
                float(row["lng"]) if row["lng"] else None,
                pop,
            ))
    conn.executemany(
        "INSERT INTO cities VALUES (?,?,?,?,?,?)", rows
    )
    conn.commit()
    print(f"Loaded {len(rows):,} rows into cities table.")


def run_sql_file(conn, filename):
    path = os.path.join(SQL_DIR, filename)
    with open(path) as f:
        sql = f.read()

    print(f"\n{'='*60}")
    print(f"  {filename}")
    print(f"{'='*60}")

    # Execute each statement separated by semicolons
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        try:
            cur = conn.execute(stmt)
            rows = cur.fetchall()
            if cur.description:
                headers = [d[0] for d in cur.description]
                col_widths = [max(len(h), max((len(str(r[i])) for r in rows), default=0))
                              for i, h in enumerate(headers)]
                fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
                print(fmt.format(*headers))
                print("  " + "  ".join("-" * w for w in col_widths))
                for row in rows:
                    print(fmt.format(*[str(v) for v in row]))
                print(f"\n  ({len(rows)} rows)")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    load_csv(conn)
    for sql_file in ["01_top75_cities.sql", "02_demand_by_region.sql", "03_summary_stats.sql"]:
        run_sql_file(conn, sql_file)
    conn.close()
    print(f"\nDatabase saved to: {DB_PATH}")
