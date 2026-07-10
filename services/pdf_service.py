import base64
import binascii
import os
import re
from io import BytesIO
from shutil import which

from services.ai_service import AIServiceError


MAX_EXTRACTED_PDF_CHARS = 120_000
MAX_OCR_PAGES = 10
DEFAULT_OCR_LANGUAGES = "eng+hin"
DEFAULT_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PROJECT_TESSDATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "tessdata")
)
PUNCTUATION_LINE_ENDINGS = tuple(".!?।:;)]}\"'")


def clean_pdf_text(text: str) -> str:
    value = str(text or "")
    value = value.replace("\x0c", "\n")
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", value)
    value = re.sub(r"([_\-=*#])\1{4,}", r"\1\1\1", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r" *\n *", "\n", value)
    value = re.sub(r"([A-Za-z])-\n([A-Za-z])", r"\1\2", value)

    cleaned_lines = []

    for raw_line in value.splitlines():
        line = raw_line.strip()

        if not line:
            if cleaned_lines and cleaned_lines[-1]:
                cleaned_lines.append("")
            continue

        line = re.sub(r"\s+([,.;:!?।])", r"\1", line)
        line = re.sub(r"([([{])\s+", r"\1", line)
        line = re.sub(r"\s+([)\]}])", r"\1", line)
        cleaned_lines.append(line)

    paragraphs = []

    for line in cleaned_lines:
        if not line:
            if paragraphs and paragraphs[-1]:
                paragraphs.append("")
            continue

        if not paragraphs or not paragraphs[-1]:
            paragraphs.append(line)
            continue

        previous = paragraphs[-1]
        is_page_marker = line.startswith("[Page ")
        is_list_item = bool(re.match(r"^(\d+[\).]|[-*•])\s+", line))
        is_table_like = "|" in line or re.search(r"\s{2,}", line)
        should_join = (
            not is_page_marker
            and not is_list_item
            and not is_table_like
            and not previous.endswith(PUNCTUATION_LINE_ENDINGS)
        )

        if should_join:
            paragraphs[-1] = f"{previous} {line}"
        else:
            paragraphs.append(line)

    cleaned = "\n".join(paragraphs)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _decode_pdf_payload(content: str) -> bytes:
    value = (content or "").strip()

    if not value:
        raise AIServiceError("The selected PDF is empty.")

    if value.startswith("data:"):
        try:
            _, value = value.split(",", 1)
        except ValueError as error:
            raise AIServiceError("The PDF upload could not be read.") from error

    try:
        return base64.b64decode(value, validate=True)
    except binascii.Error:
        # Backward compatibility for clients that send raw PDF bytes as text.
        return content.encode("latin-1", errors="ignore")


def _truncate_pdf_text(text: str) -> str:
    text = clean_pdf_text(text)

    if len(text) <= MAX_EXTRACTED_PDF_CHARS:
        return text

    return (
        text[:MAX_EXTRACTED_PDF_CHARS]
        + "\n\n[PDF text truncated because it is too large.]"
    )


def _extract_pdf_text_with_ocr(file_name: str, pdf_bytes: bytes) -> str:
    tesseract_cmd = os.getenv("TESSERACT_CMD", "").strip()

    if not tesseract_cmd and which("tesseract"):
        tesseract_cmd = "tesseract"
    elif not tesseract_cmd and os.path.exists(DEFAULT_TESSERACT_CMD):
        tesseract_cmd = DEFAULT_TESSERACT_CMD

    if not tesseract_cmd:
        raise AIServiceError(
            f"No selectable text was found in {file_name}. This looks like a scanned PDF. "
            "Install Tesseract OCR, restart the server, and upload the PDF again."
        )

    try:
        import pypdfium2 as pdfium
        import pytesseract
    except ImportError as error:
        raise AIServiceError(
            "Scanned PDF support requires OCR packages. Run pip install -r requirements.txt and try again."
        ) from error

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        document = pdfium.PdfDocument(pdf_bytes)
    except Exception as error:
        raise AIServiceError(f"{file_name} could not be opened for OCR.") from error

    pages = []
    ocr_languages = os.getenv("OCR_LANGUAGES", DEFAULT_OCR_LANGUAGES).strip()
    tessdata_dir = os.getenv("TESSDATA_DIR", "").strip()

    if not tessdata_dir and os.path.isdir(PROJECT_TESSDATA_DIR):
        tessdata_dir = PROJECT_TESSDATA_DIR

    ocr_config = f'--tessdata-dir "{tessdata_dir}"' if tessdata_dir else ""

    for index in range(min(len(document), MAX_OCR_PAGES)):
        try:
            page = document[index]
            image = page.render(scale=2).to_pil()
            page_text = pytesseract.image_to_string(
                image,
                lang=ocr_languages,
                config=ocr_config,
            ).strip()
        except Exception:
            page_text = ""

        if page_text:
            pages.append(f"[Page {index + 1} OCR]\n{page_text}")

    text = "\n\n".join(pages).strip()

    if not text:
        raise AIServiceError(
            f"OCR could not read text from {file_name}. Make sure Tesseract has these languages installed: {ocr_languages}."
        )

    if len(document) > MAX_OCR_PAGES:
        text += f"\n\n[OCR scanned only the first {MAX_OCR_PAGES} pages.]"

    return _truncate_pdf_text(text)


def extract_pdf_text(file_name: str, content: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise AIServiceError(
            "PDF support requires pypdf. Run pip install -r requirements.txt and try again."
        ) from error

    pdf_bytes = _decode_pdf_payload(content)

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
    except Exception as error:
        raise AIServiceError(f"{file_name} is not a readable PDF.") from error

    pages = []

    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""

        if page_text.strip():
            pages.append(f"[Page {index}]\n{page_text.strip()}")

    text = "\n\n".join(pages).strip()

    if not text:
        return _extract_pdf_text_with_ocr(file_name, pdf_bytes)

    return _truncate_pdf_text(text)
