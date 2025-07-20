# ai_native_systems

## Background
A Fortune 50 Manufacturer builds a Chromium-based browser, and it has been an integral part of their product lineup, requiring robust and efficient build infrastructure to keep up with its evolving complexity. With a need for more advanced solutions due to increasing build complexity and domain variety, the Fortune 50 Manufacturer sought a tool that could provide remote execution and build caching at scale.

A modular AI-native system architecture for building advanced, context-aware agents and tools. This scaffold is designed for rapid prototyping and research in AI-native software, combining Python and Rust for flexibility and performance.

## Project Structure

```
ai_native_systems/
│
├── apps/                     # Executable interfaces
│   ├── cli/                  # MVP command-line interface
│   │   └── main.py
│   └── shell/                # Future GUI or TUI interface (Rust/Iced)
│       └── src/
│
├── core/                     # Core subsystems (Python)
│   ├── context_kernel/       # Solid State Context (vector + symbolic)
│   ├── token_forge/          # Prompt decomposition & reuse
│   ├── thought_engine/       # Recursive feedback agents
│   ├── meta_prompting/       # Self-reflective layer
│   ├── eval_core/            # Output scoring and novelty detection
│   └── tool_chain/           # Tool execution and MCP interop
│
├── rust/                     # High-perf components (optional)
│   └── memory_fs/            # Future: graph memory + wasm plugin support
│
├── data/                     # Storage for memory/context traces
│   └── memory_store.json
│
├── shared/                   # Reusable logic, schema, and types
│   ├── utils/
│   ├── config/
│   └── schema/
│
├── tests/
│   └── unit/
│
├── .env
├── .gitignore
├── pyproject.toml            # Poetry or Hatch
├── Cargo.toml                # Rust crates
├── README.md
└── Makefile                  # Build & Dev shortcuts
```

## Getting Started
- Python: Use [Poetry](https://python-poetry.org/) or [Hatch](https://hatch.pypa.io/) for dependency management.
- Rust: Use [Cargo](https://doc.rust-lang.org/cargo/) for Rust components.
- See `Makefile` for common build and development commands.

## Remote Execution CLI & DevOps Integration

This project supports local and remote builds/tests using Bazel, Buck2, Goma, and Reclient via a unified Python CLI and Makefile targets.

### Usage

#### From the Makefile

```sh
make bazel-remote         # Run Bazel build with remote execution
make buck2-remote         # Run Buck2 build with remote execution
make goma-remote          # Run Goma build (as compiler wrapper)
make reclient-remote      # Run Reclient build
```

#### Directly via CLI

```sh
# Bazel
poetry run python devops/remote_exec.py bazel build //my:target --remote

# Buck2
poetry run python devops/remote_exec.py buck2 build //my:target --remote

# Goma
poetry run python devops/remote_exec.py goma build //my:target

# Reclient
poetry run python devops/remote_exec.py reclient build //my:target
```

- The CLI will check for the required tool in your PATH and print clear errors if not found.
- All output, errors, and exit codes are reported for CI/CD integration.

### CI Dashboard Integration

The remote execution CLI supports JUnit XML and JSON output for CI dashboards and test reporting.

#### JUnit XML Output

Generate JUnit XML files for CI dashboards (GitHub Actions, Jenkins, etc.):

```sh
# Bazel with JUnit output
poetry run python devops/remote_exec.py bazel build //... --junit-output=test-results/bazel-build.xml

# Buck2 with JUnit output
poetry run python devops/remote_exec.py buck2 test //... --junit-output=test-results/buck2-tests.xml

# Goma with JUnit output
poetry run python devops/remote_exec.py goma build //... --junit-output=test-results/goma-build.xml

# Reclient with JUnit output
poetry run python devops/remote_exec.py reclient build //... --junit-output=test-results/reclient-build.xml
```

#### JSON Output

Generate JSON summary files for custom dashboards or further processing:

```sh
# Bazel with JSON output
poetry run python devops/remote_exec.py bazel build //... --json-output=test-results/bazel-build.json

# Buck2 with JSON output
poetry run python devops/remote_exec.py buck2 test //... --json-output=test-results/buck2-tests.json
```

#### Combined Output

Generate both JUnit XML and JSON output simultaneously:

```sh
poetry run python devops/remote_exec.py bazel build //... \
  --junit-output=test-results/bazel-build.xml \
  --json-output=test-results/bazel-build.json
```

#### CI Workflow Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:

1. **Generates test results** with JUnit XML and JSON output
2. **Uploads artifacts** for CI dashboards:
   - `ci-dashboard-results`: Complete test results and summaries
   - `junit-test-results`: JUnit XML files for GitHub Actions test reporting
3. **Publishes test results** to GitHub using the `publish-unit-test-result-action`

#### Output Format

**JUnit XML Format:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<testsuite name="BazelBuild" tests="3">
  <testcase name="//target1" classname="BazelBuild"/>
  <testcase name="//target2" classname="BazelBuild">
    <failure message="Exit code 1">Build failed</failure>
  </testcase>
  <testcase name="//target3" classname="BazelBuild"/>
</testsuite>
```

**JSON Format:**
```json
[
  {
    "target": "//target1",
    "returncode": 0,
    "stdout": "Success",
    "stderr": ""
  },
  {
    "target": "//target2", 
    "returncode": 1,
    "stdout": "",
    "stderr": "Build failed"
  }
]
```

### Test Coverage

Test coverage for the remote execution CLI is provided in `tests/unit/test_remote_exec.py` using Typer's test runner and mocks for subprocess/shutil.

Additional tests for CI output functionality are in `tests/unit/test_ci_output.py`.

---

This scaffold is intended for rapid iteration and research. Contributions and extensions are welcome! 