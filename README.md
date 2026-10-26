# Multi-File AI Chatbot

## Supported formats
- PDF, DOCX, TXT, Markdown, CSV, Excel XLSX/XLS
- Common text/code files such as PY, JS, TS, HTML, CSS, JSON, XML, SQL, Java, C/C++, etc.
- Images: PNG, JPG/JPEG, WEBP, GIF (AI image analysis)

This does not support every possible file type. Audio, video, ZIP, legacy DOC, and many specialist formats need separate processing. Scanned PDFs may require OCR.

## Setup (Windows PowerShell)
1. Install Python if needed.
2. Open this folder in VS Code.
3. Create a virtual environment (recommended):
   `python -m venv .venv`
4. Activate it:
   `.\.venv\Scripts\Activate.ps1`
5. Install packages:
   `python -m pip install -r requirements.txt`
6. Copy `.env.example` to `.env`, then fill in your OpenAI API key and a model name available to your account.
7. Run:
   `python -m streamlit run app.py`

Keep `.env` private and never commit your real API key to GitHub.
