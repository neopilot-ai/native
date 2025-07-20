# ✅ AI-Native Systems — TODOs

## 🧱 Foundation (MVP Milestone)

- [x] CLI interface to accept prompts (`apps/cli/main.py`)
- [x] Prompt decomposition into Thinklets (`token_forge/decomposer.py`)
- [x] Recursive feedback refinement (`thought_engine/feedback_loop.py`)
- [x] Output persistence to memory store (`context_kernel/memory_store.py`)
- [x] Output evaluation scoring (`eval_core/scorer.py`)

---

## 🧠 Next Objectives

### 🔨 Core System Enhancements

- [x] Implement `core/token_forge/decomposer.py` with more intelligent semantic chunking
- [x] Add `core/thought_engine/feedback_loop.py` logic with multi-agent perspectives (critic, optimizer, verifier)
- [x] Add `core/context_kernel/memory_store.py` implementation to load, query, and traverse previous prompts and outputs

---

### 🛠 Tool Execution Layer

- [x] Create `tool_chain/executor.py` with:
  - [x] Simple tool calls via shell or REST API
  - [x] Tool registry and permission checks
  - [x] Support for chained execution (dependent tasks)

---

### 🔍 Memory & Context Features

- [x] Build `apps/cli/memory_viewer.py` to query stored outputs
- [x] Enable vector store support with embedding-based context recall
- [x] Implement contextual filtering for "related Thinklets"

---

### 🔁 Meta-Prompting Layer

- [x] Add `meta_prompting/self_reflection.py` for self-analysis
  - [x] Reflect on usefulness, tone, logical consistency
- [x] Score meta prompts using internal rubric (chain-of-thought grading)

---

### 🧪 Evaluation System

- [x] Expand `scorer.py` with:
  - [x] Embedding similarity (vs. ideal answers)
  - [x] Relevance + alignment (to prompt intent)
  - [x] Redundancy detection

---

### 🧰 DevOps / Tooling

- [x] Add full `pyproject.toml` for poetry/hatch + dependencies
- [x] Add Makefile targets (`make run`, `make test`, `make zip`)
- [x] Set up pre-commit formatting hooks (e.g., black, isort)
- [x] Add test coverage for all core modules (`tests/unit/`)
- [ ] Add support for build tools that use the Remote Execution protocol, such as:
  - [ ] Bazel
  - [ ] Buck2
  - [ ] Goma
  - [ ] Reclient
- [x] Content Addressable Storage (CAS) - Minimize redundant compilation of unchanged source code for compute-efficient builds
- [x] Conceptual Remote Execution Client/Service Outline
- [x] Add `prompt_runner.py` CLI to simulate agent execution flow
- [x] Log agent conversations as `.md` or `.jsonl` in `logs/`
- [x] CLI wrapper for `auto_commit_agent.py` with `--all` flag
- [x] Generate project documentation (conceptual)

---

## 🤖 AI-Orchestrated Development Workflows

- [x] Implement AI-assisted multi-agent orchestration
- [x] Define LLM-A (code generator), LLM-B (reviewer), LLM-C (synthesizer), LLM-D (supervisor)
- [x] Chain agents using feedback and validation loops
- [x] Enable cross-agent tool access (e.g., edit_file_tool, read_file_tool)
- [x] Build meta_prompting/prompt_strategies.py for:
  - [x] Minimalist Prompting
  - [x] Modular Decomposition Prompts
  - [x] Multi-Shot + Chain-of-Thought guidance
  - [x] Socratic Prompting
- [x] Create prompt registry and evaluation system
- [x] Track prompt ↔️ result lineage
- [x] Score prompts by clarity, conciseness, and effectiveness
- [ ] Automate GitOps tasks via agents:
  - [x] AI-generated commit messages, PR titles, and release notes
  - [x] Code linting and formatting via Prettier, ESLint, Black
  - [x] CI/CD pipeline suggestions using GitHub Actions

---

## 🧬 Future Vision

- [x] MVP GUI/TUI with Iced.rs or Tauri (`apps/shell/`)
- [x] Plugin system for tools / agents / scorers
- [x] Long-term hierarchical context store (CRDT/IPFS-based)
- [x] Interactive Workflow Debugging/Stepping
- [x] Dynamic Tool Discovery and Integration
- [x] Knowledge Graph / Ontology Integration
- [x] Made With Love In Rust - Reduce runtime errors, guarantee memory-safety without requiring garbage collection, & eliminate race conditions at any scale.

---

## 🚀 New Feature: FAANG-Level AI Developer Mode

- [x] Design and embed a multi-layered system prompt simulating a Principal Engineer's discipline, tech stack, and workflows
- [x] Create a JSON prompt template for loading as system context in AI tools
- [x] Implement logic to load and apply the JSON system prompt in your AI call pipeline (e.g., OpenAI API, Ollama)
- [x] Combine system prompt with task-specific user prompts for recursive file analysis, refactoring, security hardening, and CI/CD generation
- [x] Integrate prompt-driven AI responses into existing recursive decomposition and feedback loop modules
- [x] Persist iterative outputs for long-term project memory and meta-evaluation
- [x] AIResponseCache that caches LLM results for a time-to-live
- [ ] Develop test cases using Next.js/NestJS repos with sensitive config to validate the feature's effectiveness

---

🧠 _"From prompt to system" means building infrastructure for memory, feedback, autonomy, and interaction. Stay recursive._
