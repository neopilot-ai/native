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

---

This scaffold is intended for rapid iteration and research. Contributions and extensions are welcome! 