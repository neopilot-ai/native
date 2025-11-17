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
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

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


class BuildExecutionError(RuntimeError):
    """Raised when a build invocation returns one or more failures."""

    def __init__(self, tool: str, results):
        super().__init__(f"{tool} command reported failures")
        self.tool = tool
        self.results = results


@dataclass(frozen=True)
class ToolSpec:
    name: str
    binaries: Sequence[str]
    remote_flags: Sequence[str] = ()
    default_target: str = "//..."
    supports_remote: bool = True

    @property
    def label(self) -> str:
        return self.name.capitalize()


TOOL_SPECS: Dict[str, ToolSpec] = {
    "bazel": ToolSpec(
        name="bazel",
        binaries=("bazel",),
        remote_flags=("--config=remote",),
    ),
    "buck2": ToolSpec(
        name="buck2",
        binaries=("buck2",),
        remote_flags=("--remote-execution",),
    ),
    "goma": ToolSpec(
        name="goma",
        binaries=("goma", "gomacc"),
        default_target="//...",
        supports_remote=False,
    ),
    "reclient": ToolSpec(
        name="reclient",
        binaries=("reclient", "reproxy"),
        supports_remote=False,
    ),
}


def _ensure_parent_directory(output_path: Optional[str]):
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)


def _resolve_binary(tool: str, spec: ToolSpec) -> str:
    for candidate in spec.binaries:
        binary = shutil.which(candidate)
        if binary:
            return binary
    if len(spec.binaries) == 1:
        missing = spec.binaries[0]
    else:
        missing = " or ".join(spec.binaries)
    raise FileNotFoundError(f"'{missing}' not found in PATH")


def _format_extra_args(extra_args: Optional[Sequence[str]]) -> List[str]:
    if not extra_args:
        return []
    flattened: List[str] = []
    for arg in extra_args:
        flattened.extend(str(arg).split())
    return flattened


def run_build_tool(
    tool: str,
    command: str,
    targets: Optional[List[str]] = None,
    *,
    remote: bool = False,
    extra_args: Optional[Sequence[str]] = None,
    max_workers: int = 4,
    junit_output: Optional[str] = None,
    json_output: Optional[str] = None,
    log: Optional[Callable[[str], None]] = None,
    workdir: Optional[str] = None,
):
    """Run a build/test command for the specified tool.

    Args:
        tool: Tool identifier (bazel, buck2, goma, reclient).
        command: Command verb (build, test, run, etc.).
        targets: Explicit targets to execute. Defaults to tool default target.
        remote: Whether to enable remote execution flags when supported.
        extra_args: Additional command-line arguments.
        max_workers: Max concurrent invocations when multiple targets.
        junit_output: Optional path to emit JUnit XML summary.
        json_output: Optional path to emit JSON summary.
        log: Optional callable for streaming log messages.
        workdir: Optional working directory for subprocess invocations.

    Returns:
        A list of dictionaries describing the individual target results.

    Raises:
        FileNotFoundError: If the required tool binary cannot be located.
        BuildExecutionError: If any target returns a non-zero exit code.
    """

    spec = TOOL_SPECS[tool]
    binary_path = _resolve_binary(tool, spec)
    extra = _format_extra_args(extra_args)
    log = log or (lambda _: None)
    all_targets = targets or [spec.default_target]

    def build_command(target: str) -> List[str]:
        cmd = [binary_path, command, target]
        if remote and spec.supports_remote and spec.remote_flags:
            cmd.extend(spec.remote_flags)
        cmd.extend(extra)
        return cmd

    results = []

    def run_one(tgt: str):
        cmd = build_command(tgt)
        log(f"[{spec.label}] Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workdir,
        )
        return {
            "target": tgt,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": cmd,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futs = [executor.submit(run_one, tgt) for tgt in all_targets]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    for res in results:
        if res["stdout"]:
            log(res["stdout"].rstrip())
        if res["stderr"]:
            log(res["stderr"].rstrip())

    log(f"\n[{spec.label}] Batch Summary:")
    for res in results:
        log(f"  Target: {res['target']} | Exit: {res['returncode']}")

    if junit_output:
        _ensure_parent_directory(junit_output)
        _write_junit(results, junit_output, suite_name=f"{spec.label}Build")
        log(f"[{spec.label}] Wrote JUnit XML to {junit_output}")
    if json_output:
        _ensure_parent_directory(json_output)
        _write_json(results, json_output)
        log(f"[{spec.label}] Wrote JSON summary to {json_output}")

    if any(res["returncode"] != 0 for res in results):
        raise BuildExecutionError(spec.label, results)

    return results


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
    all_targets = _parse_targets(target, targets, targets_file)
    extra = extra_args.split() if extra_args else None

    try:
        run_build_tool(
            "bazel",
            command,
            all_targets,
            remote=remote,
            extra_args=extra,
            max_workers=max_workers,
            junit_output=junit_output,
            json_output=json_output,
            log=typer.echo,
        )
    except FileNotFoundError as err:
        typer.echo(f"[Bazel] Error: {err}")
        raise typer.Exit(1)
    except BuildExecutionError as err:
        typer.echo(f"[Bazel] {err}")
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
    all_targets = _parse_targets(target, targets, targets_file)
    extra = extra_args.split() if extra_args else None

    try:
        run_build_tool(
            "buck2",
            command,
            all_targets,
            remote=remote,
            extra_args=extra,
            max_workers=max_workers,
            junit_output=junit_output,
            json_output=json_output,
            log=typer.echo,
        )
    except FileNotFoundError as err:
        typer.echo(f"[Buck2] Error: {err}")
        raise typer.Exit(1)
    except BuildExecutionError as err:
        typer.echo(f"[Buck2] {err}")
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
    all_targets = _parse_targets(target, targets, targets_file)
    extra = extra_args.split() if extra_args else None

    try:
        run_build_tool(
            "goma",
            command,
            all_targets,
            remote=False,
            extra_args=extra,
            max_workers=max_workers,
            junit_output=junit_output,
            json_output=json_output,
            log=typer.echo,
        )
    except FileNotFoundError as err:
        typer.echo(f"[Goma] Error: {err}")
        raise typer.Exit(1)
    except BuildExecutionError as err:
        typer.echo(f"[Goma] {err}")
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
    all_targets = _parse_targets(target, targets, targets_file)
    extra = extra_args.split() if extra_args else None

    try:
        run_build_tool(
            "reclient",
            command,
            all_targets,
            remote=False,
            extra_args=extra,
            max_workers=max_workers,
            junit_output=junit_output,
            json_output=json_output,
            log=typer.echo,
        )
    except FileNotFoundError as err:
        typer.echo(f"[Reclient] Error: {err}")
        raise typer.Exit(1)
    except BuildExecutionError as err:
        typer.echo(f"[Reclient] {err}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
