import os
import json
import re


INPUT_DIR = "data/processed"
OUTPUT_DIR = "results"


def mock_llm_extract(text):
    """
    Mock LLM extraction function.
    Later, we can replace this with OpenAI, Gemini, Claude, or local LLM.
    """

    extraction = {
        "research_problem": "Identify the main research problem discussed in the paper.",
        "methodology": "Extract the methodology used by the authors.",
        "dataset": "Identify any dataset, corpus, or data source mentioned.",
        "key_contribution": "Summarize the main contribution of the research.",
        "findings": "Extract the key findings or results.",
        "limitations": "Identify limitations discussed in the paper.",
        "future_work": "Extract future research directions."
    }

    return extraction


def extract_paper_name(filename):
    """
    Gets original paper name from chunk filename.
    Example: paper1_chunk_3.txt -> paper1
    """
    return re.sub(r"_chunk_\d+\.txt$", "", filename)


def process_chunks():
    """
    Processes chunk files and creates structured extraction output.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chunk_files = [
        file for file in os.listdir(INPUT_DIR)
        if file.lower().endswith(".txt")
    ]

    if not chunk_files:
        print("No processed chunk files found.")
        return

    final_results = []

    for chunk_file in chunk_files:
        input_path = os.path.join(INPUT_DIR, chunk_file)

        with open(input_path, "r", encoding="utf-8") as f:
            chunk_text = f.read()

        extraction = mock_llm_extract(chunk_text)

        result = {
            "paper_name": extract_paper_name(chunk_file),
            "chunk_file": chunk_file,
            "model_used": "mock_llm",
            **extraction
        }

        final_results.append(result)

    output_path = os.path.join(OUTPUT_DIR, "llm_extractions.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4)

    print(f"LLM extraction completed. Results saved to {output_path}")


if __name__ == "__main__":
    process_chunks()