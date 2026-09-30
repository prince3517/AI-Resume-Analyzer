import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract selectable text from every page of a PDF."""
    document = fitz.open(pdf_path)
    pages = [page.get_text("text") for page in document]
    document.close()
    return "\n".join(pages)
