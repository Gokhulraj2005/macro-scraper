import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_FILE = "macro.db"


def save_to_db(df):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inflation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                year INTEGER NOT NULL,
                inflation_rate REAL,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (country, year)
            )
        """)
        data = [
            (row.country, int(row.year), float(row.inflation_rate))
            for row in df.itertuples(index=False)
        ]
        conn.executemany("""
            INSERT INTO inflation (country, year, inflation_rate)
            VALUES (?, ?, ?)
            ON CONFLICT(country, year) DO UPDATE SET
                inflation_rate = excluded.inflation_rate,
                scraped_at = CURRENT_TIMESTAMP
        """, data)
        conn.commit()
    finally:
        conn.close()
    return len(data)


if __name__ == "__main__":
    from scraper import fetch_page, parse_table
    from cleaner import clean_data, validate_data

    df, _ = validate_data(clean_data(parse_table(fetch_page())))
    print("Rows saved:", save_to_db(df))