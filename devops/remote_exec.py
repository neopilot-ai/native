#!/usr/bin/env python3
"""
Remote Execution CLI Wrapper for Build Tools (Bazel, Buck2, Goma, Reclient)

Allows triggering builds/tests locally or via remote execution, and reporting results.
"""

import concurrent.futures
import json as pyjson
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer()


def _parse_targets(
    target: str, targets: Optional[str], targets_file: Optional[str]
) -> list:
    if targets_file:
        with open(targets_file) as f:
            return [line.strip() for line in f if line.strip()]
    if targets:
        return [t.strip() for t in targets.split(",") if t.strip()]
    return [target]


def _write_junit(results, output_path, suite_name="BuildResults"):
    testsuite = ET.Element("testsuite", name=suite_name, tests=str(len(results)))
    for r in results:
        testcase = ET.SubElement(
            testsuite, "testcase", name=r["target"], classname=suite_name
        )
        if r["returncode"] != 0:
            failure = ET.SubElement(
                testcase, "failure", message=f"Exit code {r['returncode']}"
            )
            failure.text = r["stderr"] or r["stdout"]
    tree = ET.ElementTree(testsuite)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def _write_json(results, output_path):
    with open(output_path, "w") as f:
        pyjson.dump(results, f, indent=2)


# --- Bazel Integration ---


@app.command()
def bazel(
    command: str = typer.Argument(
        ..., help="Bazel command: build, test, run, clean, etc."
    ),
    target: str = typer.Argument("//...", help="Bazel target (default: //... for all)"),
    remote: bool = typer.Option(
        False, "--remote", help="Use remote execution (if configured)"
    ),
    extra_args: Optional[str] = typer.Option(
        None, "--extra", help="Extra Bazel args (quoted)"
    ),
    targets: Optional[str] = typer.Option(
        None, "--targets", help="Comma-separated list of targets"
    ),
    targets_file: Optional[str] = typer.Option(
        None, "--targets-file", help="File with one target per line"
    ),
    max_workers: int = typer.Option(
        4, "--max-workers", help="Max parallel builds/tests"
    ),
    junit_output: Optional[str] = typer.Option(
        None, "--junit-output", help="Write JUnit XML summary to this file"
    ),
    json_output: Optional[str] = typer.Option(
        None, "--json-output", help="Write JSON summary to this file"
    ),
):
    """
    Run Bazel build/test/run/clean on one or more targets (in parallel if multiple).
    """
    if not shutil.which("bazel"):
        typer.echo("[Bazel] Error: 'bazel' not found in PATH.")
        raise typer.Exit(1)
    all_targets = _parse_targets(target, targets, targets_file)
    results = []

    def run_one(tgt):
        bazel_cmd = ["bazel", command, tgt]
        if remote:
            bazel_cmd += ["--config=remote"]
        if extra_args:
            bazel_cmd += extra_args.split()
        typer.echo(f"[Bazel] Running: {' '.join(bazel_cmd)}")
        result = subprocess.run(bazel_cmd, capture_output=True, text=True)
        return {
            "target": tgt,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futs = [executor.submit(run_one, tgt) for tgt in all_targets]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    # Print summary
    typer.echo("\n[Bazel] Batch Summary:")
    for r in results:
        typer.echo(f"  Target: {r['target']} | Exit: {r['returncode']}")
    if junit_output:
        _write_junit(results, junit_output, suite_name="BazelBuild")
        typer.echo(f"[Bazel] Wrote JUnit XML to {junit_output}")
    if json_output:
        _write_json(results, json_output)
        typer.echo(f"[Bazel] Wrote JSON summary to {json_output}")
    if any(r["returncode"] != 0 for r in results):
        raise typer.Exit(1)


# --- Buck2 Integration ---


@app.command()
def buck2(
    command: str = typer.Argument(
        ..., help="Buck2 command: build, test, run, clean, etc."
    ),
    target: str = typer.Argument("//...", help="Buck2 target (default: //... for all)"),
    remote: bool = typer.Option(
        False, "--remote", help="Use remote execution (if configured)"
    ),
    extra_args: Optional[str] = typer.Option(
        None, "--extra", help="Extra Buck2 args (quoted)"
    ),
    targets: Optional[str] = typer.Option(
        None, "--targets", help="Comma-separated list of targets"
    ),
    targets_file: Optional[str] = typer.Option(
        None, "--targets-file", help="File with one target per line"
    ),
    max_workers: int = typer.Option(
        4, "--max-workers", help="Max parallel builds/tests"
    ),
    junit_output: Optional[str] = typer.Option(
        None, "--junit-output", help="Write JUnit XML summary to this file"
    ),
    json_output: Optional[str] = typer.Option(
        None, "--json-output", help="Write JSON summary to this file"
    ),
):
    """
    Run Buck2 build/test/run/clean on one or more targets (in parallel if multiple).
    """
    if not shutil.which("buck2"):
        typer.echo("[Buck2] Error: 'buck2' not found in PATH.")
        raise typer.Exit(1)
    all_targets = _parse_targets(target, targets, targets_file)
    results = []

    def run_one(tgt):
        buck2_cmd = ["buck2", command, tgt]
        if remote:
            buck2_cmd += ["--remote-execution"]
        if extra_args:
            buck2_cmd += extra_args.split()
        typer.echo(f"[Buck2] Running: {' '.join(buck2_cmd)}")
        result = subprocess.run(buck2_cmd, capture_output=True, text=True)
        return {
            "target": tgt,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futs = [executor.submit(run_one, tgt) for tgt in all_targets]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    typer.echo("\n[Buck2] Batch Summary:")
    for r in results:
        typer.echo(f"  Target: {r['target']} | Exit: {r['returncode']}")
    if junit_output:
        _write_junit(results, junit_output, suite_name="Buck2Build")
        typer.echo(f"[Buck2] Wrote JUnit XML to {junit_output}")
    if json_output:
        _write_json(results, json_output)
        typer.echo(f"[Buck2] Wrote JSON summary to {json_output}")
    if any(r["returncode"] != 0 for r in results):
        raise typer.Exit(1)


# --- Goma Integration ---


@app.command()
def goma(
    command: str = typer.Argument(..., help="Goma command: build, test, etc."),
    target: str = typer.Argument("//...", help="Goma target (default: //... for all)"),
    extra_args: Optional[str] = typer.Option(
        None, "--extra", help="Extra Goma args (quoted)"
    ),
    targets: Optional[str] = typer.Option(
        None, "--targets", help="Comma-separated list of targets"
    ),
    targets_file: Optional[str] = typer.Option(
        None, "--targets-file", help="File with one target per line"
    ),
    max_workers: int = typer.Option(
        4, "--max-workers", help="Max parallel builds/tests"
    ),
    junit_output: Optional[str] = typer.Option(
        None, "--junit-output", help="Write JUnit XML summary to this file"
    ),
    json_output: Optional[str] = typer.Option(
        None, "--json-output", help="Write JSON summary to this file"
    ),
):
    """
    Run Goma build/test on one or more targets (in parallel if multiple).
    """
    goma_bin = shutil.which("goma") or shutil.which("gomacc")
    if not goma_bin:
        typer.echo("[Goma] Error: 'goma' or 'gomacc' not found in PATH.")
        raise typer.Exit(1)
    all_targets = _parse_targets(target, targets, targets_file)
    results = []

    def run_one(tgt):
        goma_cmd = [goma_bin, command, tgt]
        if extra_args:
            goma_cmd += extra_args.split()
        typer.echo(f"[Goma] Running: {' '.join(goma_cmd)}")
        result = subprocess.run(goma_cmd, capture_output=True, text=True)
        return {
            "target": tgt,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futs = [executor.submit(run_one, tgt) for tgt in all_targets]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    typer.echo("\n[Goma] Batch Summary:")
    for r in results:
        typer.echo(f"  Target: {r['target']} | Exit: {r['returncode']}")
    if junit_output:
        _write_junit(results, junit_output, suite_name="GomaBuild")
        typer.echo(f"[Goma] Wrote JUnit XML to {junit_output}")
    if json_output:
        _write_json(results, json_output)
        typer.echo(f"[Goma] Wrote JSON summary to {json_output}")
    if any(r["returncode"] != 0 for r in results):
        raise typer.Exit(1)


# --- Reclient Integration ---


@app.command()
def reclient(
    command: str = typer.Argument(..., help="Reclient command: build, test, etc."),
    target: str = typer.Argument(
        "//...", help="Reclient target (default: //... for all)"
    ),
    extra_args: Optional[str] = typer.Option(
        None, "--extra", help="Extra Reclient args (quoted)"
    ),
    targets: Optional[str] = typer.Option(
        None, "--targets", help="Comma-separated list of targets"
    ),
    targets_file: Optional[str] = typer.Option(
        None, "--targets-file", help="File with one target per line"
    ),
    max_workers: int = typer.Option(
        4, "--max-workers", help="Max parallel builds/tests"
    ),
    junit_output: Optional[str] = typer.Option(
        None, "--junit-output", help="Write JUnit XML summary to this file"
    ),
    json_output: Optional[str] = typer.Option(
        None, "--json-output", help="Write JSON summary to this file"
    ),
):
    """
    Run Reclient build/test on one or more targets (in parallel if multiple).
    """
    reclient_bin = shutil.which("reclient") or shutil.which("reproxy")
    if not reclient_bin:
        typer.echo("[Reclient] Error: 'reclient' or 'reproxy' not found in PATH.")
        raise typer.Exit(1)
    all_targets = _parse_targets(target, targets, targets_file)
    results = []

    def run_one(tgt):
        reclient_cmd = [reclient_bin, command, tgt]
        if extra_args:
            reclient_cmd += extra_args.split()
        typer.echo(f"[Reclient] Running: {' '.join(reclient_cmd)}")
        result = subprocess.run(reclient_cmd, capture_output=True, text=True)
        return {
            "target": tgt,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futs = [executor.submit(run_one, tgt) for tgt in all_targets]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    typer.echo("\n[Reclient] Batch Summary:")
    for r in results:
        typer.echo(f"  Target: {r['target']} | Exit: {r['returncode']}")
    if junit_output:
        _write_junit(results, junit_output, suite_name="ReclientBuild")
        typer.echo(f"[Reclient] Wrote JUnit XML to {junit_output}")
    if json_output:
        _write_json(results, json_output)
        typer.echo(f"[Reclient] Wrote JSON summary to {json_output}")
    if any(r["returncode"] != 0 for r in results):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
