import numpy as np
from openai import OpenAI

client = OpenAI()

def make_chunks(text, size=800, overlap=120):
    """Split text into chunks with a small overlap to preserve context."""
    if not text:
        return []
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    chunks = []
    step = size - overlap
    for i in range(0, len(text), step):
        chunk = text[i:i + size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def get_embeddings(texts):
    if not texts:
        return np.empty((0, 0))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([item.embedding for item in response.data])
