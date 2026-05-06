import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI


INPUT_FILE = "results/llm_extractions.json"
OUTPUT_FILE = "results/final_smart_paper_extractions.json"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_json_output(output_text):
    output_text = output_text.strip()
    output_text = output_text.replace("```json", "")
    output_text = output_text.replace("```", "")
    output_text = output_text.strip()
    return json.loads(output_text)


def aggregate_with_llm(paper_name, chunk_outputs):
    combined_text = json.dumps(chunk_outputs, indent=2)

    prompt = f"""
You are an expert scientific literature analyst.

The following JSON contains extraction results from multiple chunks of ONE research paper.

Your task:
Combine the chunk-level outputs into ONE clean paper-level summary.

Rules:
- Remove duplicate information
- Do not invent details
- Keep only information supported by the chunk outputs
- Return ONLY valid JSON
- No markdown
- No explanation

Return this exact JSON structure:
{{
  "paper_name": "{paper_name}",
  "research_problem": "",
  "methodology": "",
  "dataset": "",
  "key_contribution": "",
  "findings": "",
  "limitations": "",
  "future_work": ""
}}

Chunk-level outputs:
{combined_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        return clean_json_output(response.output_text)

    except Exception as e:
        print(f"Smart aggregation parsing failed for {paper_name}: {e}")
        print(response.output_text)

        return {
            "paper_name": paper_name,
            "research_problem": "Parsing failed",
            "methodology": "Parsing failed",
            "dataset": "Parsing failed",
            "key_contribution": response.output_text,
            "findings": "Parsing failed",
            "limitations": "Parsing failed",
            "future_work": "Parsing failed"
        }


def smart_aggregate():
    if not os.path.exists(INPUT_FILE):
        print("Run llm_extraction.py first.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    grouped = defaultdict(list)

    for row in data:
        grouped[row["paper_name"]].append({
            "research_problem": row.get("research_problem", ""),
            "methodology": row.get("methodology", ""),
            "dataset": row.get("dataset", ""),
            "key_contribution": row.get("key_contribution", ""),
            "findings": row.get("findings", ""),
            "limitations": row.get("limitations", ""),
            "future_work": row.get("future_work", "")
        })

    final_results = []

    for paper_name, chunk_outputs in grouped.items():
        print(f"Smart aggregating: {paper_name}")
        final_result = aggregate_with_llm(paper_name, chunk_outputs)
        final_results.append(final_result)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4)

    print(f"Smart paper-level aggregation saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    smart_aggregate()