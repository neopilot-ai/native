#!/usr/bin/env python3
"""
Multi-Agent Orchestrator CLI - AI-Orchestrated Development Workflows

This tool provides a command-line interface to run multi-agent development
workflows with different agent combinations and workflow types.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from core.meta_prompting.prompt_scorer import PromptScorer
from orchestration.agent_roles import AGENTS, MultiAgentOrchestrator
from orchestration.conversation_logger import log_conversation_json, log_conversation_md
from prompting.system_prompts.faang_engineer_prompt import (
    build_combined_prompt as build_faang_prompt,
)

app = typer.Typer()


@app.command()
def workflow(
    prompt: str = typer.Argument(..., help="Development request or prompt"),
    workflow_type: str = typer.Option(
        "standard",
        "--type",
        "-t",
        help="Workflow type: standard, architectural, testing, documentation",
    ),
    enable_validation: bool = typer.Option(
        True, "--validation/--no-validation", help="Enable validation steps"
    ),
    enable_feedback: bool = typer.Option(
        True, "--feedback/--no-feedback", help="Enable feedback loops"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save results to JSON file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    faang: bool = typer.Option(
        False, "--faang", help="Use the FAANG-level developer prompt"
    ),
):
    """
    Run a complete multi-agent development workflow.
    """
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(AGENTS)

    if faang:
        system_prompt = build_faang_prompt(prompt)
    else:
        system_prompt = ""

    # Run workflow
    results = orchestrator.orchestrate_development_workflow(
        user_prompt=prompt,
        system_prompt=system_prompt,
        workflow_type=workflow_type,
        enable_validation=enable_validation,
        enable_feedback_loops=enable_feedback,
    )

    # Log conversation
    session_id = results["session_id"]
    log_conversation_md(
        conversation_id=session_id,
        agent_role="user",
        input_text=prompt,
        output_text=results["final_output"],
        metadata={"workflow_type": workflow_type},
    )
    log_conversation_json(
        conversation_id=session_id,
        agent_role="user",
        input_text=prompt,
        output_text=results["final_output"],
        metadata={"workflow_type": workflow_type},
    )

    # Display results
    if verbose:
        _display_detailed_results(results)
    else:
        _display_summary_results(results)

    # Save results if requested
    if output_file:
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        typer.echo(f"\n💾 Results saved to: {output_file}")

    return results


@app.command()
def agents():
    """
    List available agents and their roles.
    """
    typer.echo("🤖 Available Agents")
    typer.echo("=" * 50)

    for role, agent in AGENTS.items():
        typer.echo(f"\n{role.value}: {agent.name}")
        typer.echo(f"  Role: {role.name}")
        typer.echo(f"  State: {agent.state.value}")
        typer.echo(f"  Tools: {', '.join(agent.tools) if agent.tools else 'None'}")
        typer.echo(
            f"  Permissions: {', '.join(agent.permissions) if agent.permissions else 'None'}"
        )


@app.command()
def workflow_types():
    """
    List available workflow types and their descriptions.
    """
    typer.echo("🔄 Available Workflow Types")
    typer.echo("=" * 50)

    workflows = {
        "standard": {
            "description": "Complete development workflow with all agents",
            "agents": [
                "Architect",
                "Code Generator",
                "Reviewer",
                "Tester",
                "Documenter",
                "Synthesizer",
                "Supervisor",
            ],
            "steps": 9,
        },
        "architectural": {
            "description": "Focus on system architecture and high-level design",
            "agents": [
                "Architect",
                "Code Generator",
                "Reviewer",
                "Synthesizer",
                "Supervisor",
            ],
            "steps": 7,
        },
        "testing": {
            "description": "Focus on test generation and validation",
            "agents": [
                "Code Generator",
                "Tester",
                "Reviewer",
                "Synthesizer",
                "Supervisor",
            ],
            "steps": 7,
        },
        "documentation": {
            "description": "Focus on documentation and user guides",
            "agents": [
                "Code Generator",
                "Documenter",
                "Reviewer",
                "Synthesizer",
                "Supervisor",
            ],
            "steps": 7,
        },
    }

    for wf_type, info in workflows.items():
        typer.echo(f"\n{wf_type.upper()}")
        typer.echo(f"  Description: {info['description']}")
        typer.echo(f"  Agents: {', '.join(info['agents'])}")
        typer.echo(f"  Steps: {info['steps']}")


@app.command()
def demo(
    workflow_type: str = typer.Option(
        "standard", "--type", "-t", help="Workflow type to demo"
    ),
    output_dir: str = typer.Option(
        "demo_results", "--output-dir", "-o", help="Directory for demo results"
    ),
):
    """
    Run a demo workflow with sample prompts.
    """
    demo_prompts = {
        "standard": "Create a REST API endpoint for user authentication with JWT tokens",
        "architectural": "Design a microservices architecture for an e-commerce platform",
        "testing": "Generate comprehensive unit tests for a user management system",
        "documentation": "Create API documentation for a machine learning model service",
    }

    prompt = demo_prompts.get(workflow_type, demo_prompts["standard"])

    typer.echo(f"🎯 Running {workflow_type} demo workflow")
    typer.echo(f"📝 Demo prompt: {prompt}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Run workflow
    orchestrator = MultiAgentOrchestrator(AGENTS)
    results = orchestrator.orchestrate_development_workflow(
        user_prompt=prompt,
        workflow_type=workflow_type,
        enable_validation=True,
        enable_feedback_loops=True,
    )

    # Save demo results
    demo_file = (
        output_path
        / f"demo_{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(demo_file, "w") as f:
        json.dump(results, f, indent=2)

    typer.echo(f"\n✅ Demo completed!")
    typer.echo(f"📊 Final Score: {results['final_score']['overall']:.3f}")
    typer.echo(f"💾 Results saved to: {demo_file}")

    return results


@app.command()
def analyze(
    session_id: Optional[str] = typer.Option(
        None, "--session", "-s", help="Analyze specific session"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file for analysis"
    ),
):
    """
    Analyze workflow performance and agent effectiveness.
    """
    typer.echo("📊 Workflow Analysis")
    typer.echo("=" * 40)

    # This would analyze stored workflow results
    # For now, show placeholder
    typer.echo("Analysis features coming soon...")
    typer.echo("- Agent performance metrics")
    typer.echo("- Workflow efficiency analysis")
    typer.echo("- Quality trend analysis")
    typer.echo("- Bottleneck identification")


def _display_summary_results(results: dict):
    """Display summary of workflow results."""
    typer.echo(f"\n📋 Workflow Summary")
    typer.echo(f"Session ID: {results['session_id']}")
    typer.echo(f"Type: {results['workflow_type']}")
    typer.echo(f"Steps Completed: {len(results['steps'])}")
    typer.echo(f"Final Score: {results['final_score']['overall']:.3f}")
    typer.echo(f"Validation Passed: {results['context']['validation_passed']}")


def _display_detailed_results(results: dict):
    """Display detailed workflow results."""
    typer.echo(f"\n📋 Detailed Workflow Results")
    typer.echo(f"Session ID: {results['session_id']}")
    typer.echo(f"Workflow Type: {results['workflow_type']}")
    typer.echo(f"Timestamp: {results['timestamp']}")
    typer.echo(f"User Prompt: {results['user_prompt']}")

    typer.echo(f"\n📊 Final Scores:")
    for metric, score in results["final_score"].items():
        typer.echo(f"  {metric.replace('_', ' ').title()}: {score:.3f}")

    typer.echo(f"\n🔄 Workflow Steps:")
    for i, (step_name, step_result) in enumerate(results["steps"], 1):
        typer.echo(f"  {i}. {step_name.replace('_', ' ').title()}")
        if "execution_time" in step_result:
            typer.echo(f"     Time: {step_result['execution_time']:.2f}s")
        if "state" in step_result:
            typer.echo(f"     State: {step_result['state']}")

    typer.echo(f"\n📄 Final Output:")
    typer.echo(
        results["final_output"][:500] + "..."
        if len(results["final_output"]) > 500
        else results["final_output"]
    )

    typer.echo(f"\n🔍 Context:")
    typer.echo(
        f"  Conversation History Length: {results['context']['conversation_history_length']}"
    )
    typer.echo(
        f"  Shared Memory Keys: {', '.join(results['context']['shared_memory_keys']) if results['context']['shared_memory_keys'] else 'None'}"
    )
    typer.echo(f"  Validation Passed: {results['context']['validation_passed']}")


if __name__ == "__main__":
    app()
