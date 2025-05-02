# manualchat/loader.py
import fitz  # PyMuPDF
from PIL import Image
import io
import streamlit as st

def extract_chunks_from_pdf(file, max_chars=1000):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    chunks = []
    total_pages = len(doc)
    progress = st.progress(0)

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if not text:
            continue

        paragraphs = text.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            while len(para) > max_chars:
                split_point = para[:max_chars].rfind(".") + 1 or max_chars
                chunks.append((f"Side {page_num}", para[:split_point].strip()))
                para = para[split_point:]
            if para:
                chunks.append((f"Side {page_num}", para.strip()))

        progress.progress(page_num / total_pages)

    return chunks

def render_pdf_page_as_image(pdf_path, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=150)
    return Image.open(io.BytesIO(pix.tobytes("png")))
