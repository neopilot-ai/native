import os
import tempfile
import json
from core.context_kernel import memory_store

def setup_test_store(entries):
    fd, path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as f:
        json.dump(entries, f)
    return path

def test_load_and_store():
    entries = [
        {"prompt": "What is AI?", "output": "Artificial Intelligence."},
        {"prompt": "Define ML.", "output": "Machine Learning."},
        {"prompt": "What is deep learning?", "output": "A subset of ML."}
    ]
    path = setup_test_store(entries)
    loaded = memory_store.load_memory(path)
    assert loaded == entries
    os.remove(path)

def test_query_memory():
    entries = [
        {"prompt": "What is AI?", "output": "Artificial Intelligence."},
        {"prompt": "Define ML.", "output": "Machine Learning."},
        {"prompt": "What is deep learning?", "output": "A subset of ML."}
    ]
    path = setup_test_store(entries)
    # Query by prompt
    result = memory_store.query_memory("AI", by="prompt", path=path)
    assert len(result) == 1 and result[0]["prompt"] == "What is AI?"
    # Query by output
    result = memory_store.query_memory("Machine", by="output", path=path)
    assert len(result) == 1 and result[0]["output"] == "Machine Learning."
    # Query by both
    result = memory_store.query_memory("ML", by="both", path=path)
    assert len(result) == 2
    os.remove(path)

def test_traverse_memory():
    entries = [
        {"prompt": f"Prompt {i}", "output": f"Output {i}"} for i in range(10)
    ]
    path = setup_test_store(entries)
    # Get first 3
    result = memory_store.traverse_memory(0, 3, path=path)
    assert len(result) == 3 and result[0]["prompt"] == "Prompt 0"
    # Get last 2
    result = memory_store.traverse_memory(8, None, path=path)
    assert len(result) == 2 and result[1]["prompt"] == "Prompt 9"
    os.remove(path)

if __name__ == "__main__":
    test_load_and_store()
    test_query_memory()
    test_traverse_memory()
    print("All memory_store tests passed.") 