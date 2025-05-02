# manualchat/embedder.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from store import save_chunks, save_embeddings, load_embeddings, get_manual_path
import streamlit as st

model = SentenceTransformer("hkunlp/instructor-base")

def embed_in_batches(texts, batch_size=32):
    all_embeddings = []
    progress = st.progress(0)
    total = len(texts)

    for i in range(0, total, batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch)
        all_embeddings.extend(batch_embeddings)

        percent = int((i + batch_size) / total * 100)
        progress.progress(min(percent, 100))

    return np.array(all_embeddings)

def create_or_load_index(manual_name, chunks):
    base = get_manual_path(manual_name)
    index_path = f"{base}/index.faiss"

    try:
        embeddings = load_embeddings(manual_name)
        index = faiss.read_index(index_path)
    except:
        texts = [chunk[1] for chunk in chunks]
        embeddings = embed_in_batches(texts)
        save_chunks(manual_name, chunks)
        save_embeddings(manual_name, embeddings)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, index_path)

    return index

def search_chunks(manual_name, question, chunks, k=5, max_chars=7000):
    base = get_manual_path(manual_name)
    embeddings = load_embeddings(manual_name)
    index = faiss.read_index(f"{base}/index.faiss")

    q_embed = model.encode([question])[0]
    D, I = index.search(np.array([q_embed]), k)

    # Hent k kandidat-chunks
    sources = [chunks[i] for i in I[0]]

    # Generisk nøgleordsbaseret re-sortering (uden hardcoding)
    keywords = [w.strip(".,:;!?") for w in question.lower().split() if len(w) > 3]
    sources.sort(key=lambda chunk: sum(k in chunk[1].lower() for k in keywords), reverse=True)

    # Byg kontekst op til max_chars
    context = ""
    selected_sources = []
    for page, text in sources:
        if len(context) + len(text) > max_chars:
            break
        context += text + "\n\n"
        selected_sources.append((page, text))

    return context.strip(), selected_sources
