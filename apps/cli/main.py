import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.token_forge.decompose import decompose_prompt
from core.tool_chain.executor import ToolExecutor
from core.context_kernel.memory_store import store_output
from orchestration.agent_roles import MultiAgentOrchestrator, AGENTS
from prompting.system_prompts.faang_engineer_prompt import (
    build_combined_prompt as build_faang_prompt,
)
from prompting.system_prompts.principal_engineer_prompt import (
    build_combined_prompt as build_principal_prompt,
)

console = Console()

app = typer.Typer()


def greet(name: str) -> str:
    """Simple greeting function for demo purposes."""
    return f"Hello, {name}!"


def run_workflow(
    prompt: str,
    system_prompt: str,
    workflow_type: str,
    enable_feedback: bool,
    enable_eval: bool,
    debug_mode: bool = False,
) -> dict:
    """Execute the main development workflow."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Initializing workflow...", total=None)
            
            # Initialize the orchestrator
            orchestrator = MultiAgentOrchestrator(AGENTS)
            
            # Execute the workflow
            progress.update(task, description="Executing workflow...")
            result = orchestrator.orchestrate_development_workflow(
                user_prompt=prompt,
                system_prompt=system_prompt,
                workflow_type=workflow_type,
                enable_validation=enable_eval,
                enable_feedback_loops=enable_feedback,
                debug_mode=debug_mode,
            )
            
            # Store the result for future reference
            store_output(
                prompt=prompt,
                output=str(result),
                metadata={
                    "workflow_type": workflow_type,
                    "feedback_enabled": enable_feedback,
                    "evaluation_enabled": enable_eval,
                },
            )
            
            progress.update(task, description="Workflow completed!", completed=1)
            return result
            
    except Exception as e:
        console.print(f"[red]Error in workflow execution: {str(e)}[/red]")
        if debug_mode:
            import traceback
            console.print(traceback.format_exc())
        return {"error": str(e), "status": "failed"}


@app.command()
def main(
    prompt: str = typer.Argument(..., help="Input prompt for the AI system"),
    workflow_type: str = typer.Option(
        "standard",
        "--workflow-type",
        "-w",
        help="Type of workflow (standard, architectural, testing, documentation)",
    ),
    feedback: bool = typer.Option(
        False, "--feedback", "-f", help="Enable feedback/counter-feedback loop"
    ),
    tools: bool = typer.Option(
        False, "--tools", "-t", help="Enable toolchain execution"
    ),
    eval: bool = typer.Option(
        False, "--eval", "-e", help="Enable output evaluation"
    ),
    faang: bool = typer.Option(
        False, "--faang", help="Use the FAANG-level developer prompt"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug mode with detailed output"
    ),
):
    """
    AI Native Systems CLI - A multi-agent development environment.
    
    Example usage:
        python -m apps.cli.main "Implement a REST API" --workflow-type architectural --faang
    """
    # Set up system prompt
    try:
        if faang:
            system_prompt_path = "prompting/system_prompts/faang_engineer_prompt.json"
            combined_prompt = build_faang_prompt(prompt, system_prompt_path)
        else:
            system_prompt_path = "prompting/system_prompts/principal_engineer_prompt.json"
            combined_prompt = build_principal_prompt(prompt, system_prompt_path)

        if debug:
            console.print("[bold]=== System Prompt ===[/bold]")
            console.print(combined_prompt)
            console.print("\n[bold]=== Thinklets ===[/bold]")
            thinklets = decompose_prompt(prompt)
            for i, t in enumerate(thinklets, 1):
                console.print(f"  {i}. {t}")
            console.print("\n")

        # Run the main workflow
        result = run_workflow(
            prompt=prompt,
            system_prompt=combined_prompt,
            workflow_type=workflow_type,
            enable_feedback=feedback,
            enable_eval=eval,
            debug_mode=debug,
        )

        # Display results
        console.print("\n[bold green]=== Workflow Results ===[/bold green]")
        if isinstance(result, dict):
            console.print_json(data=result)
        else:
            console.print(result)

        # Demo tool execution if requested
        if tools:
            console.print("\n[bold]=== Tool Execution ===[/bold]")
            executor = ToolExecutor()
            executor.register_tool("greet", greet)
            tool_result = executor.execute("greet", prompt)
            console.print(f"[tool] greet result: {tool_result}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if debug:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


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
