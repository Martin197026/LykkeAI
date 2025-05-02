# manualchat/store.py
import os
import json
import numpy as np
import re

DATA_DIR = "data"

def sanitize_filename(name):
    # Fjerner ulovlige tegn i filnavne
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

def get_manual_path(manual_name):
    safe_name = sanitize_filename(manual_name.replace(".pdf", ""))
    base = os.path.join(DATA_DIR, safe_name)
    os.makedirs(base, exist_ok=True)
    return base

def save_chunks(manual_name, chunks):
    base = get_manual_path(manual_name)
    with open(os.path.join(base, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def load_manual_chunks(manual_name):
    base = get_manual_path(manual_name)
    with open(os.path.join(base, "chunks.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def save_embeddings(manual_name, embeddings):
    base = get_manual_path(manual_name)
    np.save(os.path.join(base, "embeddings.npy"), embeddings)

def load_embeddings(manual_name):
    base = get_manual_path(manual_name)
    return np.load(os.path.join(base, "embeddings.npy"))

def list_manuals():
    if not os.path.exists(DATA_DIR):
        return []
    return [name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))]
