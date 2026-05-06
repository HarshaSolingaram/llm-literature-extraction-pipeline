import sqlite3
import pandas as pd
import os


CSV_FILE = "results/llm_extractions.csv"
DB_FILE = "results/literature_pipeline.db"


def create_connection():
    return sqlite3.connect(DB_FILE)


def load_csv_to_database():
    if not os.path.exists(CSV_FILE):
        print("CSV file not found. Run export_results.py first.")
        return

    df = pd.read_csv(CSV_FILE)

    conn = create_connection()

    df.to_sql(
        "llm_extractions",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("Data loaded into SQLite database successfully.")
    print(f"Database created at: {DB_FILE}")
    print(f"Rows inserted: {len(df)}")


if __name__ == "__main__":
    load_csv_to_database()