import json
from pathlib import Path

import typer

from core.token_forge.decompose import decompose_prompt
from core.tool_chain.executor import ToolExecutor
from prompting.system_prompts.faang_engineer_prompt import (
    build_combined_prompt as build_faang_prompt,
)
from prompting.system_prompts.principal_engineer_prompt import (
    build_combined_prompt as build_principal_prompt,
)

app = typer.Typer()


def greet(name):
    return f"Hello, {name}!"


@app.command()
def main(
    prompt: str = typer.Argument(..., help="Input prompt for the AI system"),
    feedback: bool = typer.Option(
        False, "--feedback", help="Enable feedback/counter-feedback loop"
    ),
    tools: bool = typer.Option(False, "--tools", help="Enable toolchain execution"),
    eval: bool = typer.Option(False, "--eval", help="Enable output evaluation"),
    faang: bool = typer.Option(
        False, "--faang", help="Use the FAANG-level developer prompt"
    ),
):
    """
    CLI entry point for ai_native_systems.
    """
    if faang:
        system_prompt_path = "prompting/system_prompts/faang_engineer_prompt.json"
        combined_prompt = build_faang_prompt(prompt, system_prompt_path)
    else:
        system_prompt_path = "prompting/system_prompts/principal_engineer_prompt.json"
        combined_prompt = build_principal_prompt(prompt, system_prompt_path)

    print(f"Combined Prompt:\n{combined_prompt}\n")
    # Placeholder for LLM agent call
    # result = your_llm_call(combined_prompt)
    # print(result)

    thinklets = decompose_prompt(prompt)
    print("Thinklets:")
    for i, t in enumerate(thinklets, 1):
        print(f"  {i}. {t}")

    if tools:
        executor = ToolExecutor()
        executor.register_tool("greet", greet)
        # For demo, use the prompt as the name to greet
        result = executor.execute("greet", prompt)
        print(f"[ToolExecutor] greet result: {result}")
    # TODO: Call the main pipeline here


@app.command()
def memory_viewer(
    path: str = typer.Option(
        "data/memory_store.json", help="Path to memory store JSON"
    ),
    search: str = typer.Option(None, help="Search term to filter prompts"),
    page: int = typer.Option(1, help="Page number (1-based)"),
    page_size: int = typer.Option(5, help="Number of results per page"),
):
    """Browse past prompts and outputs from the memory store, with search and pagination."""
    store_path = Path(path)
    if not store_path.exists():
        typer.echo(f"No memory store found at {path}")
        raise typer.Exit()
    with open(store_path, "r") as f:
        try:
            data = json.load(f)
        except Exception as e:
            typer.echo(f"Error reading memory store: {e}")
            raise typer.Exit()
    if not data:
        typer.echo("No prompts found in memory store.")
        raise typer.Exit()
    # Filter by search term if provided
    if search:
        data = [
            entry for entry in data if search.lower() in entry.get("prompt", "").lower()
        ]
    total = len(data)
    if total == 0:
        typer.echo("No prompts match your search.")
        raise typer.Exit()
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    page_data = data[start:end]
    typer.echo(
        f"Showing {start+1}-{min(end, total)} of {total} results " f"(Page {page})\n"
    )
    for i, entry in enumerate(page_data, start + 1):
        prompt = entry.get("prompt", "<no prompt>")
        output = entry.get("output", "<no output>")
        typer.echo(f"{i}. Prompt: {prompt}")
        typer.echo(f"   Output: {output}\n")
    if end < total:
        typer.echo(f"Use --page {page+1} to see more results.")


if __name__ == "__main__":
    app()
