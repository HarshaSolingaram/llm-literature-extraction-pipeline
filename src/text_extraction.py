import os
import fitz  # PyMuPDF


RAW_PDF_DIR = "data/raw_pdfs"
OUTPUT_DIR = "data/extracted_text"


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using PyMuPDF.
    """
    text = ""

    try:
        document = fitz.open(pdf_path)

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text()
            text += f"\n\n--- Page {page_number} ---\n\n"
            text += page_text

        document.close()
        return text

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None


def process_all_pdfs():
    """
    Reads all PDFs from data/raw_pdfs and saves extracted text
    into data/extracted_text.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf_files = [
        file for file in os.listdir(RAW_PDF_DIR)
        if file.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print("No PDF files found in data/raw_pdfs.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(RAW_PDF_DIR, pdf_file)
        output_filename = pdf_file.replace(".pdf", ".txt")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        extracted_text = extract_text_from_pdf(pdf_path)

        if extracted_text:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)

            print(f"Extracted text saved: {output_path}")


if __name__ == "__main__":
    process_all_pdfs()