#!/usr/bin/env python3
"""
Prompt Runner CLI - Simulate agent execution flow for AI-native systems.

This tool provides a command-line interface to run prompts through the full
agent pipeline including decomposition, feedback loops, and memory storage.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from core.context_kernel.memory_store import query_memory_by_embedding, store_output
from core.eval_core.scorer import OutputScorer
from core.meta_prompting.prompt_strategies import (
    MinimalistPrompting,
    ModularDecompositionPrompts,
    MultiShotChainOfThoughtGuidance,
    SocraticPrompting,
)
from core.meta_prompting.self_reflection import self_reflect
from core.thought_engine.feedback_loop import multi_agent_feedback
from core.token_forge.decomposer import decompose_prompt
from orchestration.agent_roles import AGENTS, AgentRole
from orchestration.conversation_logger import log_conversation_md
from prompting.system_prompts.faang_engineer_prompt import (
    build_combined_prompt as build_faang_prompt,
)

app = typer.Typer()


@app.command()
def run(
    prompt: str = typer.Argument(
        ..., help="The prompt to process through the agent pipeline"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="File to save results"
    ),
    enable_feedback: bool = typer.Option(
        True, "--feedback/--no-feedback", help="Enable feedback loop"
    ),
    enable_scoring: bool = typer.Option(
        True, "--score/--no-score", help="Enable output scoring"
    ),
    enable_memory: bool = typer.Option(
        True, "--memory/--no-memory", help="Enable memory storage"
    ),
    enable_reflection: bool = typer.Option(
        True, "--reflect/--no-reflect", help="Enable self-reflection"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    faang: bool = typer.Option(
        False, "--faang", help="Use the FAANG-level developer prompt"
    ),
    minimalist: bool = typer.Option(
        False, "--minimalist", help="Apply minimalist prompting strategy"
    ),
    modular: bool = typer.Option(
        False, "--modular", help="Apply modular decomposition prompting strategy"
    ),
    cot: bool = typer.Option(
        False, "--cot", help="Apply multi-shot chain-of-thought guidance strategy"
    ),
    socratic: bool = typer.Option(
        False, "--socratic", help="Apply socratic prompting strategy"
    ),
):
    """
    Run a prompt through the complete agent pipeline.
    """
    session_id = str(uuid.uuid4())[:8]
    results = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "pipeline_steps": {},
    }

    if faang:
        system_prompt = build_faang_prompt(prompt)
    else:
        system_prompt = ""

    # Apply prompting strategies
    if minimalist:
        prompt = MinimalistPrompting().apply(prompt)
    if modular:
        prompt = ModularDecompositionPrompts().apply(prompt)
    if cot:
        prompt = MultiShotChainOfThoughtGuidance().apply(prompt)
    if socratic:
        prompt = SocraticPrompting().apply(prompt)

    typer.echo(f"🚀 Starting agent pipeline (Session: {session_id})")
    typer.echo(
        f"📝 Processing prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
    )

    # Step 1: Prompt Decomposition
    typer.echo("\n🔧 Step 1: Decomposing prompt into thinklets...")
    thinklets = decompose_prompt(prompt)
    results["pipeline_steps"]["decomposition"] = {
        "thinklets": thinklets,
        "count": len(thinklets),
    }

    if verbose:
        for i, thinklet in enumerate(thinklets, 1):
            typer.echo(f"   Thinklet {i}: {thinklet}")

    # Step 2: Multi-Agent Feedback (if enabled)
    if enable_feedback:
        typer.echo("\n🔄 Step 2: Running multi-agent feedback loop...")
        feedback_results = multi_agent_feedback(thinklets, system_prompt=system_prompt)
        results["pipeline_steps"]["feedback"] = feedback_results

        if verbose:
            for i, feedback in enumerate(feedback_results, 1):
                typer.echo(f"   Thinklet {i} feedback:")
                typer.echo(f"     Critic: {feedback['critic']}")
                typer.echo(f"     Optimizer: {feedback['optimizer']}")
                typer.echo(f"     Verifier: {feedback['verifier']}")

    # Step 3: Agent Chain Execution
    typer.echo("\n🤖 Step 3: Executing agent chain...")
    intermediate = prompt
    agent_results = []

    for role in [
        AgentRole.CODE_GENERATOR,
        AgentRole.REVIEWER,
        AgentRole.SYNTHESIZER,
        AgentRole.SUPERVISOR,
    ]:
        agent = AGENTS[role]
        if verbose:
            typer.echo(f"   Running {role.value}...")

        response = agent.execute(intermediate)
        agent_results.append(
            {"role": role.value, "input": intermediate, "output": response}
        )
        intermediate = response

    results["pipeline_steps"]["agent_chain"] = agent_results
    final_output = intermediate

    # Step 4: Self-Reflection (if enabled)
    if enable_reflection:
        typer.echo("\n🧠 Step 4: Performing self-reflection...")
        reflection = self_reflect(final_output)
        results["pipeline_steps"]["reflection"] = reflection

        if verbose:
            typer.echo(f"   Usefulness: {reflection['scores']['usefulness']}/2")
            typer.echo(f"   Tone: {reflection['scores']['tone']}/2")
            typer.echo(
                f"   Logical Consistency: {reflection['scores']['logical_consistency']}/2"
            )

    # Step 5: Output Scoring (if enabled)
    if enable_scoring:
        typer.echo("\n📊 Step 5: Scoring output...")
        scorer = OutputScorer()
        score = scorer.score_output(final_output, prompt)
        results["pipeline_steps"]["scoring"] = {
            "overall_score": score.overall_score,
            "relevance_score": score.relevance_score,
            "coherence_score": score.coherence_score,
            "completeness_score": score.completeness_score,
            "embedding_similarity": score.embedding_similarity,
            "redundancy_penalty": score.redundancy_penalty,
        }

        if verbose:
            typer.echo(f"   Overall Score: {score.overall_score:.3f}")
            typer.echo(f"   Relevance: {score.relevance_score:.3f}")
            typer.echo(f"   Coherence: {score.coherence_score:.3f}")
            typer.echo(f"   Completeness: {score.completeness_score:.3f}")

    # Step 6: Memory Storage (if enabled)
    if enable_memory:
        typer.echo("\n💾 Step 6: Storing in memory...")
        store_output(prompt, final_output)
        results["pipeline_steps"]["memory"] = {"stored": True}

    # Step 7: Contextual Recall
    typer.echo("\n🔍 Step 7: Finding related contexts...")
    related_contexts = query_memory_by_embedding(prompt, top_k=3)
    results["pipeline_steps"]["contextual_recall"] = {
        "related_contexts": len(related_contexts),
        "contexts": (
            related_contexts[:2] if related_contexts else []
        ),  # Limit for output
    }

    if verbose and related_contexts:
        typer.echo(f"   Found {len(related_contexts)} related contexts")
        for i, context in enumerate(related_contexts[:2], 1):
            typer.echo(f"   Context {i}: {context.get('prompt', '')[:50]}...")

    # Final Output
    typer.echo(f"\n✅ Pipeline completed!")
    typer.echo(f"📄 Final Output:\n{final_output}")

    # Save results if output file specified
    if output_file:
        output_path = Path(output_file)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        typer.echo(f"\n💾 Results saved to: {output_file}")

    # Log conversation
    log_conversation_md(session_id, "user", prompt, final_output)

    return results


@app.command()
def batch(
    prompts_file: str = typer.Argument(
        ..., help="JSON file containing list of prompts"
    ),
    output_dir: str = typer.Option(
        "batch_results", "--output-dir", "-o", help="Directory for results"
    ),
    **kwargs,
):
    """
    Run multiple prompts in batch mode.
    """
    prompts_path = Path(prompts_file)
    if not prompts_path.exists():
        typer.echo(f"❌ Prompts file not found: {prompts_file}")
        raise typer.Exit(1)

    with open(prompts_path, "r") as f:
        prompts_data = json.load(f)

    if isinstance(prompts_data, list):
        prompts = prompts_data
    elif isinstance(prompts_data, dict) and "prompts" in prompts_data:
        prompts = prompts_data["prompts"]
    else:
        typer.echo(
            "❌ Invalid prompts file format. Expected list or dict with 'prompts' key."
        )
        raise typer.Exit(1)

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    typer.echo(f"🚀 Running batch processing for {len(prompts)} prompts...")

    all_results = []
    for i, prompt in enumerate(prompts, 1):
        typer.echo(f"\n📝 Processing prompt {i}/{len(prompts)}...")
        try:
            result = run.callback(prompt, **kwargs)
            all_results.append(result)
        except Exception as e:
            typer.echo(f"❌ Error processing prompt {i}: {e}")
            continue

    # Save batch results
    batch_file = (
        output_path / f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(batch_file, "w") as f:
        json.dump(
            {
                "batch_info": {
                    "total_prompts": len(prompts),
                    "successful": len(all_results),
                    "timestamp": datetime.now().isoformat(),
                },
                "results": all_results,
            },
            f,
            indent=2,
        )

    typer.echo(f"\n✅ Batch processing completed!")
    typer.echo(f"📊 Processed: {len(all_results)}/{len(prompts)} prompts successfully")
    typer.echo(f"💾 Results saved to: {batch_file}")


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
    Analyze pipeline performance and results.
    """
    typer.echo("📊 Pipeline Analysis")
    typer.echo("=" * 40)

    # This would analyze stored results and provide insights
    # For now, just show a placeholder
    typer.echo("Analysis features coming soon...")
    typer.echo("- Performance metrics")
    typer.echo("- Quality trends")
    typer.echo("- Agent effectiveness")
    typer.echo("- Memory utilization")


if __name__ == "__main__":
    app()
