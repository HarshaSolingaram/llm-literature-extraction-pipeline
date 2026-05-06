import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI


INPUT_DIR = "data/processed"
OUTPUT_DIR = "results"
DEBUG_DIR = "results/debug_previews"

MODEL_NAME = "gpt-4.1-mini"
INTERACTIVE_MODE = False

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_json_output(output_text):
    """
    Removes markdown wrapping and converts LLM output into JSON.
    """

    output_text = output_text.strip()
    output_text = output_text.replace("```json", "")
    output_text = output_text.replace("```", "")
    output_text = output_text.strip()

    return json.loads(output_text)


def preview_chunk_text(chunk_file, chunk_text, preview_chars=1500):
    """
    Shows and saves chunk preview before sending it to the LLM.
    """

    os.makedirs(DEBUG_DIR, exist_ok=True)

    print("\n" + "=" * 90)
    print(f"PREVIEWING CHUNK: {chunk_file}")
    print("=" * 90)
    print(chunk_text[:preview_chars])
    print("\n" + "=" * 90)
    print(f"Total characters in chunk: {len(chunk_text)}")
    print("=" * 90 + "\n")

    preview_path = os.path.join(
        DEBUG_DIR,
        chunk_file.replace(".txt", "_preview.txt")
    )

    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(chunk_text[:preview_chars])


def real_llm_extract(text):
    """
    Sends cleaned section-aware chunk text to OpenAI and extracts structured fields.
    """

    prompt = f"""
You are an expert scientific literature analyst.

Extract structured research knowledge from the paper text below.

Rules:
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT invent information.
- If a field is missing, write "Not clearly mentioned".
- Output must start with {{ and end with }}.

Return this exact JSON structure:
{{
  "research_problem": "",
  "methodology": "",
  "dataset": "",
  "key_contribution": "",
  "findings": "",
  "limitations": "",
  "future_work": ""
}}

Paper text:
{text}
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt
    )

    try:
        return clean_json_output(response.output_text)

    except Exception as e:
        print(f"JSON parsing failed: {e}")
        print("Raw LLM output:")
        print(response.output_text)

        return {
            "research_problem": "Parsing failed",
            "methodology": "Parsing failed",
            "dataset": "Parsing failed",
            "key_contribution": response.output_text,
            "findings": "Parsing failed",
            "limitations": "Parsing failed",
            "future_work": "Parsing failed"
        }


def extract_paper_name(filename):
    """
    Extracts original paper name from section-aware chunk filename.

    Example:
    paper1_abstract_chunk_1.txt -> paper1
    paper1_introduction_chunk_2.txt -> paper1
    """

    filename = filename.replace(".txt", "")

    filename = re.sub(
        r"_(metadata_title_authors|abstract|introduction|related_work|background|literature_review|methodology|method|methods|approach|dataset|data|experiment|experiments|experimental_setup|results|evaluation|discussion|limitations|conclusion|future_work)_chunk_\d+$",
        "",
        filename,
        flags=re.IGNORECASE
    )

    return filename


def process_chunks(interactive_preview=INTERACTIVE_MODE):
    """
    Processes all section-aware chunks and creates chunk-level LLM extraction output.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chunk_files = sorted([
        file for file in os.listdir(INPUT_DIR)
        if file.lower().endswith(".txt")
    ])

    if not chunk_files:
        print("No processed chunk files found.")
        return

    final_results = []

    for chunk_file in chunk_files:
        input_path = os.path.join(INPUT_DIR, chunk_file)

        with open(input_path, "r", encoding="utf-8") as f:
            chunk_text = f.read()

        preview_chunk_text(chunk_file, chunk_text)

        if interactive_preview:
            user_choice = input("Send this chunk to LLM? (y/n/q): ").lower().strip()

            if user_choice == "q":
                print("Stopping pipeline.")
                break

            if user_choice == "n":
                print(f"Skipped: {chunk_file}")
                continue

        extraction = real_llm_extract(chunk_text)

        result = {
            "paper_name": extract_paper_name(chunk_file),
            "chunk_file": chunk_file,
            "model_used": MODEL_NAME,
            **extraction
        }

        final_results.append(result)

        print(f"Processed by LLM: {chunk_file}")

    output_path = os.path.join(OUTPUT_DIR, "llm_extractions.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4)

    print(f"Chunk-level LLM extraction saved to {output_path}")


if __name__ == "__main__":
    process_chunks(interactive_preview=INTERACTIVE_MODE)