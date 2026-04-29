import os
import re


INPUT_DIR = "data/extracted_text"
OUTPUT_DIR = "data/processed"


def clean_text(text):
    """
    Cleans extracted PDF text by removing unnecessary noise.
    """
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"--- Page \d+ ---", "", text)
    text = re.sub(r"References\s+.*", "", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()


def chunk_text(text, chunk_size=1500, overlap=200):
    """
    Splits long paper text into overlapping chunks.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def process_text_files():
    """
    Cleans extracted text files and saves chunked output.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    text_files = [
        file for file in os.listdir(INPUT_DIR)
        if file.lower().endswith(".txt")
    ]

    if not text_files:
        print("No extracted text files found.")
        return

    for text_file in text_files:
        input_path = os.path.join(INPUT_DIR, text_file)

        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)

        base_name = text_file.replace(".txt", "")

        for i, chunk in enumerate(chunks, start=1):
            output_path = os.path.join(
                OUTPUT_DIR,
                f"{base_name}_chunk_{i}.txt"
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(chunk)

        print(f"Processed {text_file}: {len(chunks)} chunks created.")


if __name__ == "__main__":
    process_text_files()