import json
import pandas as pd
import os


INPUT_FILE = "results/llm_extractions.json"
OUTPUT_FILE = "results/llm_extractions.csv"


def export_json_to_csv():
    if not os.path.exists(INPUT_FILE):
        print("llm_extractions.json not found. Run llm_extraction.py first.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"CSV export completed: {OUTPUT_FILE}")
    print(f"Total records exported: {len(df)}")


if __name__ == "__main__":
    export_json_to_csv()