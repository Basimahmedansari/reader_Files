from pathlib import Path
from pypdf import PdfReader
from docx import Document
import pandas as pd

TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".html",
    ".css", ".json", ".xml", ".yaml", ".yml", ".sql", ".log",
    ".java", ".c", ".cpp", ".h", ".cs", ".php", ".rb", ".go",
    ".rs", ".sh", ".ps1"
}

def read_file(uploaded_file):
    """Extract readable text from supported document and text files."""
    name = uploaded_file.name.lower()
    suffix = Path(name).suffix

    if suffix == ".pdf":
        reader = PdfReader(uploaded_file)
        parts = []
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                parts.append(f"[Page {page_num}]\n{page_text}")
        return "\n\n".join(parts)

    if suffix == ".docx":
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if suffix in {".xlsx", ".xls"}:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        parts = []
        for sheet_name, frame in sheets.items():
            parts.append(f"[Sheet: {sheet_name}]\n{frame.fillna('').to_string(index=False)}")
        return "\n\n".join(parts)

    if suffix == ".csv":
        frame = pd.read_csv(uploaded_file)
        return frame.fillna("").to_string(index=False)

    if suffix in TEXT_EXTENSIONS:
        raw = uploaded_file.getvalue()
        for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")

    raise ValueError(
        f"Unsupported file type: {suffix or 'unknown'}. "
        "Supported: PDF, DOCX, TXT, CSV, XLSX and common text/code files."
    )
