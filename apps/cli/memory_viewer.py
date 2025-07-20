import csv
import json
from pathlib import Path

import typer

from core.context_kernel.memory_store import (
    load_memory,
    query_memory,
    query_memory_by_embedding,
)
from core.context_kernel.vector_store import ContextualVectorStore

app = typer.Typer()


@app.command()
def browse(
    search: str = typer.Option(None, help="Search term for prompt/output"),
    by: str = typer.Option("both", help="Search in 'prompt', 'output', or 'both'"),
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(5, help="Results per page"),
    path: str = typer.Option("data/memory_store.json", help="Path to memory store"),
):
    """
    Browse and search memory store.
    """
    if search:
        entries = query_memory(search, by=by, path=path)
    else:
        entries = load_memory(path)
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size
    page_entries = entries[start:end]
    typer.echo(        f"Showing {start+1}-{min(end, total)} of {total} results "        f"(Page {page})\n"    )
    for i, entry in enumerate(page_entries, start=start + 1):
        typer.echo(f"{i}. Prompt: {entry.get('prompt', '<no prompt>')}")
        typer.echo(f"   Output: {entry.get('output', '<no output>')}\n")
    if end < total:
        typer.echo(f"Use --page {page+1} to see more results.")


@app.command()
def search_embedding(
    query: str = typer.Argument(
        ..., help="Query string for embedding similarity search"
    ),
    top_k: int = typer.Option(5, help="Number of top similar results to return"),
    path: str = typer.Option("data/memory_store.json", help="Path to memory store"),
):
    """
    Search memory store for top-k most similar entries to the query using embedding similarity.
    """
    results = query_memory_by_embedding(query, path=path, key="prompt_emb", top_k=top_k)
    if not results:
        typer.echo("No similar entries found.")
        raise typer.Exit()
    typer.echo(
        f"Top {len(results)} similar entries to: '{query}'
"
    )
    for i, entry in enumerate(results, start=1):
        typer.echo(f"{i}. Prompt: {entry.get('prompt', '<no prompt>')}")
        typer.echo(f"   Output: {entry.get('output', '<no output>')}\n")


@app.command()
def view(
    index: int = typer.Argument(..., help="Index of the entry to view (1-based)"),
    path: str = typer.Option("data/memory_store.json", help="Path to memory store"),
):
    """
    View details for a specific entry by index.
    """
    entries = load_memory(path)
    if 1 <= index <= len(entries):
        entry = entries[index - 1]
        typer.echo(json.dumps(entry, indent=2))
    else:
        typer.echo(f"Index {index} is out of range (1-{len(entries)}).")


@app.command()
def delete(
    index: int = typer.Argument(..., help="Index of the entry to delete (1-based)"),
    path: str = typer.Option("data/memory_store.json", help="Path to memory store"),
):
    """
    Delete an entry by index.
    """
    entries = load_memory(path)
    if 1 <= index <= len(entries):
        entry = entries.pop(index - 1)
        with open(path, "w") as f:
            json.dump(entries, f, indent=2)
        typer.echo(f"Deleted entry {index}:")
        typer.echo(json.dumps(entry, indent=2))
    else:
        typer.echo(f"Index {index} is out of range (1-{len(entries)}).")


@app.command()
def export(
    search: str = typer.Option(None, help="Search term for prompt/output"),
    by: str = typer.Option("both", help="Search in 'prompt', 'output', or 'both'"),
    output: str = typer.Option(..., help="Output file path (.json or .csv)"),
    path: str = typer.Option("data/memory_store.json", help="Path to memory store"),
):
    """
    Export (filtered) entries to a JSON or CSV file.
    """
    if search:
        entries = query_memory(search, by=by, path=path)
    else:
        entries = load_memory(path)
    out_path = Path(output)
    if out_path.suffix == ".json":
        with open(out_path, "w") as f:
            json.dump(entries, f, indent=2)
        typer.echo(f"Exported {len(entries)} entries to {output} (JSON)")
    elif out_path.suffix == ".csv":
        if entries:
            keys = list(entries[0].keys())
            with open(out_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(entries)
            typer.echo(f"Exported {len(entries)} entries to {output} (CSV)")
        else:
            typer.echo("No entries to export.")
    else:
        typer.echo("Output file must end with .json or .csv")


@app.command()
def vector_search(
    query: str = typer.Argument(..., help="Query string for vector similarity search"),
    k: int = typer.Option(5, help="Number of results to return"),
    category: str = typer.Option(None, help="Filter by category"),
    tags: str = typer.Option(None, help="Filter by tags (comma-separated)"),
    min_score: float = typer.Option(None, help="Minimum quality score"),
    store_path: str = typer.Option("data/vector_store", help="Path to vector store"),
):
    """
    Search vector store using semantic similarity.
    """
    try:
        vector_store = ContextualVectorStore(store_path=store_path)

        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        results = vector_store.search_thinklets(
            query=query, k=k, category=category, tags=tag_list, min_score=min_score
        )

        if not results:
            typer.echo("No similar entries found.")
            return

        typer.echo(f"Found {len(results)} similar entries for: '{query}'\n")

        for i, result in enumerate(results, 1):
            entry = result.entry
            typer.echo(f"{i}. [Similarity: {result.similarity:.3f}]")
            typer.echo(f"   ID: {entry.id}")
            typer.echo(f"   Text: {entry.text}")
            typer.echo(f"   Category: {entry.metadata.get('category', 'unknown')}")
            typer.echo(f"   Tags: {', '.join(entry.metadata.get('tags', []))}")
            if entry.metadata.get("score"):
                typer.echo(f"   Quality Score: {entry.metadata.get('score'):.3f}")
            typer.echo(f"   Timestamp: {entry.timestamp}")
            typer.echo()

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def vector_stats(
    store_path: str = typer.Option("data/vector_store", help="Path to vector store"),
):
    """
    Show vector store statistics.
    """
    try:
        vector_store = ContextualVectorStore(store_path=store_path)
        stats = vector_store.stats()

        typer.echo("📊 Vector Store Statistics")
        typer.echo("=" * 30)
        typer.echo(f"Total Entries: {stats['total_entries']}")
        typer.echo(f"Index Size: {stats['index_size']}")
        typer.echo(f"Dimension: {stats['dimension']}")
        typer.echo(f"Model: {stats['model_name']}")
        typer.echo(f"Store Path: {stats['store_path']}")
        typer.echo(f"Model Available: {'✅' if stats['has_model'] else '❌'}")
        typer.echo(f"Index Available: {'✅' if stats['has_index'] else '❌'}")

        # Show categories
        categories = vector_store.get_categories()
        if categories:
            typer.echo(f"\n📂 Categories ({len(categories)}):")
            for cat in categories:
                typer.echo(f"  • {cat}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def vector_add(
    prompt: str = typer.Argument(..., help="Prompt text"),
    output: str = typer.Argument(..., help="Output text"),
    category: str = typer.Option("general", help="Category for the thinklet"),
    tags: str = typer.Option(None, help="Tags (comma-separated)"),
    score: float = typer.Option(None, help="Quality score (0-1)"),
    store_path: str = typer.Option("data/vector_store", help="Path to vector store"),
):
    """
    Add a new thinklet to the vector store.
    """
    try:
        vector_store = ContextualVectorStore(store_path=store_path)

        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]

        prompt_id, output_id = vector_store.add_thinklet(
            prompt=prompt, output=output, category=category, tags=tag_list, score=score
        )

        # Save the store
        vector_store.save()

        typer.echo(f"✅ Added thinklet to vector store")
        typer.echo(f"   Prompt ID: {prompt_id}")
        typer.echo(f"   Output ID: {output_id}")
        typer.echo(f"   Category: {category}")
        if tag_list:
            typer.echo(f"   Tags: {', '.join(tag_list)}")
        if score:
            typer.echo(f"   Score: {score}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def vector_export(
    output: str = typer.Argument(..., help="Output file path (.json)"),
    store_path: str = typer.Option("data/vector_store", help="Path to vector store"),
):
    """
    Export vector store summary to JSON.
    """
    try:
        vector_store = ContextualVectorStore(store_path=store_path)
        vector_store.export_context_summary(output)
        typer.echo(f"✅ Exported vector store summary to {output}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
