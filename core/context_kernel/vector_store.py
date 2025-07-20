"""
Vector store implementation for AI-native systems.

Provides embedding-based storage and retrieval for contextual memory,
enabling similarity search and related context discovery.
"""

import json
import os
import pickle
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer

    VECTOR_SUPPORT = True
except ImportError:
    VECTOR_SUPPORT = False


@dataclass
class VectorEntry:
    """Individual entry in the vector store."""

    id: str
    text: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """Result from vector similarity search."""

    entry: VectorEntry
    similarity: float
    distance: float


class VectorStore:
    """
    Vector store for embedding-based context storage and retrieval.

    Features:
    - Automatic text embedding generation
    - FAISS-based similarity search
    - Persistent storage and loading
    - Contextual filtering and metadata search
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        store_path: str = "data/vector_store",
        dimension: Optional[int] = None,
    ):
        """
        Initialize the vector store.

        Args:
            model_name: Name of the sentence transformer model
            store_path: Directory path for persistent storage
            dimension: Vector dimension (auto-detected if None)
        """
        self.model_name = model_name
        self.store_path = store_path
        self.dimension = dimension

        # Initialize components
        self.model = None
        self.index = None
        self.entries: Dict[str, VectorEntry] = {}

        # Create storage directory
        os.makedirs(store_path, exist_ok=True)

        # Load model and index
        self._initialize_model()
        self._load_or_create_index()

    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if not VECTOR_SUPPORT:
            print(
                "⚠️  Vector support not available. Install sentence-transformers and faiss-cpu."
            )
            return

        try:
            self.model = SentenceTransformer(self.model_name)
            if self.dimension is None:
                # Get dimension from model
                test_embedding = self.model.encode(["test"])
                self.dimension = test_embedding.shape[1]

            print(
                f"✅ Initialized vector model: {self.model_name} (dim={self.dimension})"
            )

        except Exception as e:
            print(f"❌ Failed to initialize model: {e}")
            self.model = None

    def _load_or_create_index(self):
        """Load existing FAISS index or create new one."""
        if not VECTOR_SUPPORT or not self.model:
            return

        index_path = os.path.join(self.store_path, "faiss_index")
        entries_path = os.path.join(self.store_path, "entries.pkl")

        try:
            # Try to load existing index and entries
            if os.path.exists(index_path) and os.path.exists(entries_path):
                self.index = faiss.read_index(index_path)
                with open(entries_path, "rb") as f:
                    self.entries = pickle.load(f)
                print(f"✅ Loaded existing index with {len(self.entries)} entries")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(
                    self.dimension
                )  # Inner product (cosine similarity)
                print(f"✅ Created new FAISS index (dim={self.dimension})")

        except Exception as e:
            print(f"⚠️  Error with index: {e}. Creating new index.")
            self.index = faiss.IndexFlatIP(self.dimension) if VECTOR_SUPPORT else None

    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        entry_id: Optional[str] = None,
    ) -> str:
        """
        Add text to the vector store.

        Args:
            text: Text content to add
            metadata: Optional metadata dictionary
            entry_id: Optional custom ID (auto-generated if None)

        Returns:
            Entry ID of the added text
        """
        if not self.model or not self.index:
            print("❌ Vector store not properly initialized")
            return None

        if entry_id is None:
            entry_id = str(uuid.uuid4())

        try:
            # Generate embedding
            embedding = self.model.encode([text])[0]
            embedding = embedding / np.linalg.norm(embedding)  # Normalize

            # Create entry
            entry = VectorEntry(
                id=entry_id, text=text, embedding=embedding, metadata=metadata or {}
            )

            # Add to index
            self.index.add(embedding.reshape(1, -1))
            self.entries[entry_id] = entry

            return entry_id

        except Exception as e:
            print(f"❌ Error adding text to vector store: {e}")
            return None

    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for similar texts in the vector store.

        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity threshold
            metadata_filter: Optional metadata filters

        Returns:
            List of SearchResult objects
        """
        if not self.model or not self.index:
            print("❌ Vector store not properly initialized")
            return []

        if self.index.ntotal == 0:
            print("⚠️  Vector store is empty")
            return []

        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)

            # Search index
            similarities, indices = self.index.search(
                query_embedding.reshape(1, -1),
                min(k * 2, self.index.ntotal),  # Get more results for filtering
            )

            # Convert results
            results = []
            entry_list = list(self.entries.values())

            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue

                if idx >= len(entry_list):
                    continue

                entry = entry_list[idx]

                # Apply threshold filter
                if similarity < threshold:
                    continue

                # Apply metadata filter
                if metadata_filter and not self._matches_metadata_filter(
                    entry.metadata, metadata_filter
                ):
                    continue

                results.append(
                    SearchResult(
                        entry=entry,
                        similarity=float(similarity),
                        distance=float(1.0 - similarity),
                    )
                )

            # Sort by similarity and limit results
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:k]

        except Exception as e:
            print(f"❌ Error searching vector store: {e}")
            return []

    def _matches_metadata_filter(
        self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]
    ) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False

            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False

        return True

    def get_by_id(self, entry_id: str) -> Optional[VectorEntry]:
        """Get entry by ID."""
        return self.entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        """
        Delete entry by ID.

        Note: This marks the entry as deleted but doesn't remove from FAISS index
        for performance reasons. Use rebuild_index() to clean up.
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False

    def get_related_contexts(
        self, text: str, k: int = 3, exclude_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Get contexts related to the given text.

        Args:
            text: Reference text
            k: Number of related contexts to return
            exclude_ids: IDs to exclude from results

        Returns:
            List of related SearchResult objects
        """
        results = self.search(text, k=k * 2)  # Get more results for filtering

        if exclude_ids:
            results = [r for r in results if r.entry.id not in exclude_ids]

        return results[:k]

    def save(self) -> bool:
        """Save the vector store to disk."""
        if not self.index or not VECTOR_SUPPORT:
            return False

        try:
            index_path = os.path.join(self.store_path, "faiss_index")
            entries_path = os.path.join(self.store_path, "entries.pkl")

            # Save FAISS index
            faiss.write_index(self.index, index_path)

            # Save entries (without embeddings to save space)
            entries_to_save = {}
            for entry_id, entry in self.entries.items():
                entry_copy = VectorEntry(
                    id=entry.id,
                    text=entry.text,
                    metadata=entry.metadata,
                    timestamp=entry.timestamp,
                )
                entries_to_save[entry_id] = entry_copy

            with open(entries_path, "wb") as f:
                pickle.dump(entries_to_save, f)

            # Save metadata
            metadata = {
                "model_name": self.model_name,
                "dimension": self.dimension,
                "total_entries": len(self.entries),
                "last_saved": datetime.now().isoformat(),
            }

            with open(os.path.join(self.store_path, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"✅ Saved vector store with {len(self.entries)} entries")
            return True

        except Exception as e:
            print(f"❌ Error saving vector store: {e}")
            return False

    def rebuild_index(self) -> bool:
        """
        Rebuild the FAISS index from scratch.
        Useful after deletions or index corruption.
        """
        if not self.model or not VECTOR_SUPPORT:
            return False

        try:
            print("🔄 Rebuilding vector index...")

            # Create new index
            self.index = faiss.IndexFlatIP(self.dimension)

            # Re-add all entries
            for entry in self.entries.values():
                if entry.embedding is None:
                    # Re-generate embedding if missing
                    embedding = self.model.encode([entry.text])[0]
                    embedding = embedding / np.linalg.norm(embedding)
                    entry.embedding = embedding

                self.index.add(entry.embedding.reshape(1, -1))

            print(f"✅ Rebuilt index with {len(self.entries)} entries")
            return True

        except Exception as e:
            print(f"❌ Error rebuilding index: {e}")
            return False

    def stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_entries": len(self.entries),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model_name": self.model_name,
            "store_path": self.store_path,
            "has_model": self.model is not None,
            "has_index": self.index is not None,
        }

    def clear(self) -> bool:
        """Clear all entries from the vector store."""
        try:
            self.entries.clear()
            if self.index:
                self.index = faiss.IndexFlatIP(self.dimension)
            print("✅ Cleared vector store")
            return True
        except Exception as e:
            print(f"❌ Error clearing vector store: {e}")
            return False


class ContextualVectorStore(VectorStore):
    """
    Enhanced vector store with contextual filtering capabilities.

    Extends VectorStore with features for organizing and filtering
    contexts by categories, topics, and temporal relationships.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_categories = set()

    def add_thinklet(
        self,
        prompt: str,
        output: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        score: Optional[float] = None,
    ) -> Tuple[str, str]:
        """
        Add a prompt-output pair (Thinklet) to the vector store.

        Args:
            prompt: Original prompt/query
            output: AI-generated output
            category: Category for organization
            tags: Optional tags for filtering
            score: Optional quality score

        Returns:
            Tuple of (prompt_id, output_id)
        """
        tags = tags or []

        # Add category to tracking
        self.context_categories.add(category)

        # Create metadata
        base_metadata = {
            "type": "thinklet",
            "category": category,
            "tags": tags,
            "score": score,
        }

        # Add prompt
        prompt_metadata = {**base_metadata, "part": "prompt"}
        prompt_id = self.add_text(prompt, prompt_metadata)

        # Add output with reference to prompt
        output_metadata = {**base_metadata, "part": "output", "prompt_id": prompt_id}
        output_id = self.add_text(output, output_metadata)

        return prompt_id, output_id

    def search_thinklets(
        self,
        query: str,
        k: int = 5,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Search for Thinklets with contextual filtering.

        Args:
            query: Search query
            k: Number of results
            category: Filter by category
            tags: Filter by tags (must have all tags)
            min_score: Minimum quality score

        Returns:
            List of SearchResult objects
        """
        metadata_filter = {"type": "thinklet"}

        if category:
            metadata_filter["category"] = category

        results = self.search(query, k=k * 3, metadata_filter=metadata_filter)

        # Additional filtering
        filtered_results = []
        for result in results:
            entry = result.entry

            # Tag filtering
            if tags:
                entry_tags = entry.metadata.get("tags", [])
                if not all(tag in entry_tags for tag in tags):
                    continue

            # Score filtering
            if min_score and entry.metadata.get("score", 0) < min_score:
                continue

            filtered_results.append(result)

        return filtered_results[:k]

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return sorted(list(self.context_categories))

    def export_context_summary(self, filepath: str) -> None:
        """Export a summary of contexts to file."""
        summary = {
            "total_entries": len(self.entries),
            "categories": self.get_categories(),
            "stats_by_category": {},
            "recent_entries": [],
        }

        # Category stats
        for category in self.context_categories:
            cat_entries = [
                e
                for e in self.entries.values()
                if e.metadata.get("category") == category
            ]
            summary["stats_by_category"][category] = len(cat_entries)

        # Recent entries (last 10)
        recent = sorted(self.entries.values(), key=lambda e: e.timestamp, reverse=True)[
            :10
        ]

        for entry in recent:
            summary["recent_entries"].append(
                {
                    "id": entry.id,
                    "text_preview": (
                        entry.text[:100] + "..."
                        if len(entry.text) > 100
                        else entry.text
                    ),
                    "category": entry.metadata.get("category", "unknown"),
                    "timestamp": entry.timestamp,
                }
            )

        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Exported context summary to {filepath}")


if __name__ == "__main__":
    # Demo usage
    store = ContextualVectorStore()

    # Add some sample thinklets
    store.add_thinklet(
        "What is machine learning?",
        "Machine learning is a subset of AI that enables systems to learn from data.",
        category="ai_concepts",
        tags=["ml", "ai", "definition"],
    )

    store.add_thinklet(
        "Explain neural networks",
        "Neural networks are computing systems inspired by biological neural networks.",
        category="ai_concepts",
        tags=["neural", "ai", "deep_learning"],
    )

    # Search for related contexts
    results = store.search_thinklets("artificial intelligence", k=2)

    for result in results:
        print(f"Similarity: {result.similarity:.3f}")
        print(f"Text: {result.entry.text}")
        print(f"Category: {result.entry.metadata.get('category')}")
        print("---")

    # Save the store
    store.save()
