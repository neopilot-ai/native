import json
from pathlib import Path
from typing import Any, List, Dict, Optional

def store_output(prompt: str, output: Any, path: str = "data/memory_store.json"):
    """
    Append the prompt and output to the memory store JSON file.
    """
    store_path = Path(path)
    if store_path.exists():
        with open(store_path, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append({"prompt": prompt, "output": output})
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

def query_memory(query: str, by: str = "both", path: str = "data/memory_store.json") -> List[Dict[str, Any]]:
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
        return [e for e in entries if query in e.get("prompt", "").lower() or query in e.get("output", "").lower()]

def traverse_memory(start: int = 0, end: Optional[int] = None, path: str = "data/memory_store.json") -> List[Dict[str, Any]]:
    """
    Return a slice of memory entries for traversal or pagination.
    """
    entries = load_memory(path)
    return entries[start:end] 