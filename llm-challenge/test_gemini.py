# test_gemini.py
import os
import pprint
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

# Load config-like values from env (or hardcode for local test)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION = os.getenv("QDRANT_COLLECTION_NAME_GEMINI", "rag_documents_gemini")

if not GEMINI_API_KEY:
    raise SystemExit("Set GEMINI_API_KEY before running this test")

# configure genai
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text):
    # This function is tolerant for different response shapes
    resp = genai.embed_content(model=GEMINI_EMBEDDING_MODEL, content=text)
    # try common variants:
    if isinstance(resp, dict) and "embedding" in resp:
        return resp["embedding"]
    if hasattr(resp, "embedding"):
        return resp.embedding
    if hasattr(resp, "data") and len(resp.data) > 0 and hasattr(resp.data[0], "embedding"):
        return resp.data[0].embedding
    # last effort - print resp and raise:
    pprint.pprint(resp)
    raise RuntimeError("Cannot parse embedding response")

# Qdrant client
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)

print("Getting embedding dimension from Gemini...")
emb = get_embedding("Hello Gemini!")
print("Embedding dim:", len(emb))

# Create collection if missing
collections = [c.name for c in qdrant.get_collections().collections]
if COLLECTION not in collections:
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=len(emb), distance=Distance.COSINE)
    )
    print("Created collection:", COLLECTION)
else:
    print("Collection already exists:", COLLECTION)

# Test upsert & search
vec = get_embedding("This is a test document")
qdrant.upsert(collection_name=COLLECTION, points=[{"id": 1, "vector": vec, "payload": {"content": "Test doc"}}])
print("Inserted test doc")

results = qdrant.search(collection_name=COLLECTION, query_vector=get_embedding("What is this doc about?"), limit=1)
print("Search results:")
pprint.pprint(results)
