import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from pdf_reader import read_file
from embeddings import make_chunks, get_embeddings
from rag import search

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")

st.set_page_config(page_title="Multi-File AI Chatbot", page_icon="📚")
st.title("📚 Multi-File AI Chatbot")
st.caption("Upload supported documents or an image, then ask questions about it.")

if not api_key:
    st.error("OPENAI_API_KEY is missing. Add it to your .env file and restart the app.")
    st.stop()
if not LLM_MODEL:
    st.error("OPENAI_LLM_MODEL is missing. Add a supported model name to your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

SUPPORTED_DOCS = [
    "pdf", "docx", "txt", "md", "csv", "xlsx", "xls", "py", "js",
    "jsx", "ts", "tsx", "html", "css", "json", "xml", "yaml", "yml",
    "sql", "log", "java", "c", "cpp", "h", "cs", "php", "rb", "go",
    "rs", "sh", "ps1"
]
IMAGE_TYPES = ["png", "jpg", "jpeg", "webp", "gif"]

uploaded_files = st.file_uploader(
    "Upload documents or images",
    type=SUPPORTED_DOCS + IMAGE_TYPES,
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded in uploaded_files:
        suffix = Path(uploaded.name).suffix.lower()

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
            if st.button(f"Analyze image: {uploaded.name}", key=f"img_{uploaded.name}"):
                with st.spinner("Analyzing image..."):
                    try:
                        import base64
                        mime = {
                            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                            ".png": "image/png", ".webp": "image/webp",
                            ".gif": "image/gif"
                        }.get(suffix, "image/png")
                        encoded = base64.b64encode(uploaded.getvalue()).decode("utf-8")
                        response = client.responses.create(
                            model=LLM_MODEL,
                            input=[{
                                "role": "user",
                                "content": [
                                    {"type": "input_text", "text": "Describe this image and explain its visible content clearly."},
                                    {"type": "input_image", "image_url": f"data:{mime};base64,{encoded}"}
                                ]
                            }]
                        )
                        st.subheader(f"Image analysis: {uploaded.name}")
                        st.write(response.output_text)
                    except Exception as e:
                        st.error(f"Could not analyze image: {e}")

    doc_files = [f for f in uploaded_files if Path(f.name).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}]
    if doc_files:
        selected = st.selectbox("Choose a document to ask questions about", doc_files, format_func=lambda f: f.name)
        if st.button("Read selected file", key="read_doc"):
            try:
                text = read_file(selected)
                if not text.strip():
                    st.error("No readable text was found. If this is a scanned PDF, OCR is needed.")
                else:
                    st.session_state["active_file_name"] = selected.name
                    st.session_state["active_file_text"] = text
                    st.session_state["active_chunks"] = make_chunks(text)
                    st.session_state.pop("active_embeddings", None)
                    st.success(f"Read {selected.name}: {len(st.session_state['active_chunks'])} text chunks created.")
            except Exception as e:
                st.error(f"Could not read this file: {e}")

if st.session_state.get("active_file_text"):
    st.subheader(f"Ask about: {st.session_state['active_file_name']}")
    if st.button("Prepare search index", key="prepare_index"):
        with st.spinner("Creating embeddings..."):
            try:
                st.session_state["active_embeddings"] = get_embeddings(st.session_state["active_chunks"])
                st.success("Ready! Ask your question below.")
            except Exception as e:
                st.error(f"Could not create embeddings: {e}")

    question = st.text_input("Ask a question about the selected file")
    if st.button("Ask AI", key="ask_ai") and question.strip():
        if "active_embeddings" not in st.session_state:
            st.warning("First click 'Prepare search index'.")
        else:
            with st.spinner("Searching file and generating answer..."):
                try:
                    relevant_chunks = search(
                        question,
                        st.session_state["active_chunks"],
                        st.session_state["active_embeddings"]
                    )
                    context = "\n\n".join(relevant_chunks)
                    prompt = f"""Answer the question using only the provided file context.
If the answer is not available in the context, say: "Answer not found in the file."

File context:
{context}

Question: {question}"""
                    response = client.responses.create(model=LLM_MODEL, input=prompt)
                    st.subheader("🤖 Answer")
                    st.write(response.output_text)
                    with st.expander("View retrieved context"):
                        st.write(context)
                except Exception as e:
                    st.error(f"Could not answer the question: {e}")
