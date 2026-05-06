import json
import pandas as pd
import os


INPUT_FILE = "results/final_smart_paper_extractions.json"
OUTPUT_FILE = "results/final_smart_paper_extractions.csv"


def export_json_to_csv():
    if not os.path.exists(INPUT_FILE):
        print("Final smart aggregation JSON not found. Run smart_aggregation.py first.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"CSV export completed: {OUTPUT_FILE}")
    print(f"Total paper-level records exported: {len(df)}")


if __name__ == "__main__":
    export_json_to_csv()