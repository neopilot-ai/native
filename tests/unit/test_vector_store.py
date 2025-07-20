import os
import tempfile

import pytest

from core.context_kernel.vector_store import SearchResult, VectorEntry, VectorStore


def test_vector_store_initialization():
    """Test vector store initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)
        assert store is not None
        assert store.store_path == temp_dir


def test_add_and_search_thinklet():
    """Test adding and searching thinklets."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add a thinklet
        thinklet_id = store.add_thinklet(
            "What is machine learning?",
            "Machine learning is a subset of AI that enables systems to learn from data.",
            category="ai_concepts",
            tags=["ml", "ai"],
        )

        assert thinklet_id is not None

        # Search for similar thinklets
        results = store.search_thinklets("artificial intelligence", k=1)

        assert len(results) > 0
        assert isinstance(results[0], SearchResult)
        assert results[0].similarity > 0.0


def test_add_thinklet_with_metadata():
    """Test adding thinklet with metadata."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        metadata = {
            "category": "programming",
            "difficulty": "intermediate",
            "tags": ["python", "algorithms"],
        }

        thinklet_id = store.add_thinklet(
            "How to implement quicksort?",
            "Quicksort is a divide-and-conquer algorithm...",
            metadata=metadata,
        )

        assert thinklet_id is not None

        # Retrieve the entry
        entry = store.get_thinklet(thinklet_id)
        assert entry is not None
        assert entry.metadata["category"] == "programming"
        assert entry.metadata["difficulty"] == "intermediate"


def test_search_by_category():
    """Test searching thinklets by category."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add thinklets with different categories
        store.add_thinklet("AI concept", "AI explanation", category="ai")
        store.add_thinklet(
            "Programming concept", "Programming explanation", category="programming"
        )

        # Search by category
        ai_results = store.search_by_category("ai", k=5)
        programming_results = store.search_by_category("programming", k=5)

        assert len(ai_results) > 0
        assert len(programming_results) > 0


def test_search_by_tags():
    """Test searching thinklets by tags."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add thinklets with different tags
        store.add_thinklet("ML concept", "ML explanation", tags=["ml", "ai"])
        store.add_thinklet(
            "Python concept", "Python explanation", tags=["python", "programming"]
        )

        # Search by tags
        ml_results = store.search_by_tags(["ml"], k=5)
        python_results = store.search_by_tags(["python"], k=5)

        assert len(ml_results) > 0
        assert len(python_results) > 0


def test_save_and_load():
    """Test saving and loading vector store."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add some thinklets
        store.add_thinklet("Test 1", "Content 1", category="test")
        store.add_thinklet("Test 2", "Content 2", category="test")

        # Save the store
        store.save()

        # Create new store instance and load
        new_store = VectorStore(store_path=temp_dir)

        # Check if data was loaded
        assert len(new_store.entries) > 0


def test_get_statistics():
    """Test getting store statistics."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add some thinklets
        store.add_thinklet("Test 1", "Content 1", category="test1")
        store.add_thinklet("Test 2", "Content 2", category="test2")
        store.add_thinklet("Test 3", "Content 3", category="test1")

        stats = store.get_statistics()

        assert stats["total_entries"] == 3
        assert "categories" in stats
        assert "tags" in stats


def test_delete_thinklet():
    """Test deleting a thinklet."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = VectorStore(store_path=temp_dir)

        # Add a thinklet
        thinklet_id = store.add_thinklet(
            "Test delete", "Content to delete", category="test"
        )

        # Verify it exists
        assert store.get_thinklet(thinklet_id) is not None

        # Delete it
        success = store.delete_thinklet(thinklet_id)
        assert success

        # Verify it's gone
        assert store.get_thinklet(thinklet_id) is None


if __name__ == "__main__":
    pytest.main([__file__])
