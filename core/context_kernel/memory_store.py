import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional imports for vector store functionality
try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    VECTOR_SUPPORT = True
except ImportError:
    VECTOR_SUPPORT = False
    print(
        "⚠️  Vector store support not available. Install sentence-transformers and faiss-cpu for full functionality."
    )

# Initialize embedding model (can be moved to config if needed)
EMBEDDING_MODEL = None
if VECTOR_SUPPORT:
    try:
        EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        print(f"⚠️  Failed to load embedding model: {e}")


# Helper to compute embedding
def compute_embedding(text: str) -> List[float]:
    if not VECTOR_SUPPORT or EMBEDDING_MODEL is None:
        # Return a simple hash-based embedding as fallback
        return [hash(text) % 1000 / 1000.0] * 384  # 384-dimensional fallback
    return EMBEDDING_MODEL.encode([text])[0].tolist()


def store_output(prompt: str, output: Any, path: str = "data/memory_store.json"):
    """
    Append the prompt and output to the memory store JSON file, with embeddings.
    """
    store_iterative_output(
        session_id="default_session",
        agent_role="default_agent",
        prompt=prompt,
        output=output,
        parent_id=None,
        path=path,
    )


def store_iterative_output(
    session_id: str,
    agent_role: str,
    prompt: str,
    output: Any,
    reasoning: Optional[str] = None,
    parent_id: Optional[str] = None,
    path: str = "data/memory_store.json",
):
    """
    Append the prompt and output to the memory store JSON file, with embeddings and lineage.
    """
    store_path = Path(path)
    if store_path.exists():
        with open(store_path, "r") as f:
            data = json.load(f)
    else:
        data = []
    prompt_emb = compute_embedding(prompt)
    output_emb = compute_embedding(str(output))
    data.append(
        {
            "session_id": session_id,
            "agent_role": agent_role,
            "parent_id": parent_id,
            "prompt": prompt,
            "output": output,
            "reasoning": reasoning,
            "prompt_emb": prompt_emb,
            "output_emb": output_emb,
        }
    )
    with open(store_path, "w") as f:
        json.dump(data, f, indent=2)


def load_memory(path: str = "data/memory_store.json") -> List[Dict[str, Any]]:
    """
    Load all memory entries from the store.
    """
    store_path = Path(path)
    if not store_path.exists():
        return []
    with open(store_path, "r") as f:
        return json.load(f)


def query_memory(
    query: str, by: str = "both", path: str = "data/memory_store.json"
) -> List[Dict[str, Any]]:
    """
    Query memory entries by substring in prompt, output, or both.
    """
    entries = load_memory(path)
    query = query.lower()
    if by == "prompt":
        return [e for e in entries if query in e.get("prompt", "").lower()]
    elif by == "output":
        return [e for e in entries if query in e.get("output", "").lower()]
    else:
        return [
            e
            for e in entries
            if query in e.get("prompt", "").lower()
            or query in e.get("output", "").lower()
        ]


def traverse_memory(
    start: int = 0, end: Optional[int] = None, path: str = "data/memory_store.json"
) -> List[Dict[str, Any]]:
    """
    Return a slice of memory entries for traversal or pagination.
    """
    entries = load_memory(path)
    return entries[start:end]


# --- Vector search logic ---
def build_faiss_index(
    entries: List[Dict[str, Any]], key: str = "prompt_emb"
) -> Optional[Any]:
    if not VECTOR_SUPPORT:
        return None
    if not entries:
        return None
    vecs = np.array([e[key] for e in entries if key in e], dtype=np.float32)
    if len(vecs) == 0:
        return None
    index = faiss.IndexFlatL2(vecs.shape[1])
    index.add(vecs)
    return index


def query_memory_by_embedding(
    query: str,
    path: str = "data/memory_store.json",
    key: str = "prompt_emb",
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most similar memory entries to the query string using vector similarity.
    """
    if not VECTOR_SUPPORT:
        # Fallback to simple text search
        return query_memory(query, by="both", path=path)[:top_k]

    entries = load_memory(path)
    if not entries:
        return []
    index = build_faiss_index(entries, key=key)
    if index is None:
        return []
    query_emb = np.array([compute_embedding(query)], dtype=np.float32)
    D, I = index.search(query_emb, top_k)
    results = []
    for idx in I[0]:
        if 0 <= idx < len(entries):
            results.append(entries[idx])
    return results
