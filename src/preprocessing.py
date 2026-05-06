import os
import re


INPUT_DIR = "data/extracted_text"
OUTPUT_DIR = "data/processed"


def clean_text(text):
    """
    Cleans raw extracted PDF text while preserving useful research paper structure.
    """

    # Remove page markers added during extraction
    text = re.sub(r"--- Page \d+ ---", "", text)

    # Remove common ACL/proceedings header noise
    text = re.sub(
        r"Proceedings of .*?Association for Computational Linguistics.*?©\d{4} Association for Computational Linguistics",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove affiliation symbols / decorative symbols
    text = re.sub(r"[♠♣♡♥♦★☆✔✘✓❌†‡§]", "", text)

    # Fix broken hyphenated words: assis- tants -> assistants
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

    # Remove email-like text
    text = re.sub(r"\S+@\S+", "", text)

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove references section
    text = re.sub(
        r"\bReferences\b.*",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    return text.strip()


def split_into_sections(text):
    """
    Splits paper text into logical research sections.
    """

    section_patterns = [
        "Abstract",
        "Introduction",
        "Related Work",
        "Background",
        "Literature Review",
        "Methodology",
        "Method",
        "Methods",
        "Approach",
        "Dataset",
        "Data",
        "Experiment",
        "Experiments",
        "Experimental Setup",
        "Results",
        "Evaluation",
        "Discussion",
        "Limitations",
        "Conclusion",
        "Future Work"
    ]

    pattern = r"\b(" + "|".join(section_patterns) + r")\b"

    parts = re.split(pattern, text, flags=re.IGNORECASE)

    sections = []

    if parts[0].strip():
        sections.append(("Metadata_Title_Authors", parts[0].strip()))

    for i in range(1, len(parts), 2):
        section_title = parts[i].strip()
        section_body = parts[i + 1].strip() if i + 1 < len(parts) else ""

        if section_body:
            sections.append((section_title, section_body))

    return sections


def chunk_section(section_title, section_text, chunk_size=3000, overlap=300):
    """
    Chunks each section separately instead of blindly slicing the full paper.
    """

    chunks = []
    start = 0

    while start < len(section_text):
        end = start + chunk_size
        chunk = section_text[start:end].strip()

        if chunk:
            formatted_chunk = f"SECTION: {section_title}\n\n{chunk}"
            chunks.append(formatted_chunk)

        start += chunk_size - overlap

    return chunks


def clear_old_processed_files():
    """
    Removes old processed chunks before creating new ones.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".txt"):
            os.remove(os.path.join(OUTPUT_DIR, file))


def process_text_files():
    clear_old_processed_files()

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
        sections = split_into_sections(cleaned_text)

        base_name = text_file.replace(".txt", "")
        chunk_count = 0

        for section_title, section_text in sections:
            chunks = chunk_section(section_title, section_text)

            clean_section_name = re.sub(
                r"\W+",
                "_",
                section_title.lower()
            ).strip("_")

            for i, chunk in enumerate(chunks, start=1):
                chunk_count += 1

                output_path = os.path.join(
                    OUTPUT_DIR,
                    f"{base_name}_{clean_section_name}_chunk_{i}.txt"
                )

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(chunk)

        print(f"Processed {text_file}: {chunk_count} section-aware chunks created.")


if __name__ == "__main__":
    process_text_files()