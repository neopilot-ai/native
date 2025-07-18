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
- [ ] Add `core/thought_engine/feedback_loop.py` logic with multi-agent perspectives (critic, optimizer, verifier)  # (in-progress)
- [x] Add `core/context_kernel/memory_store.py` implementation to load, query, and traverse previous prompts and outputs

---

### 🛠 Tool Execution Layer

- [x] Create `tool_chain/executor.py` with:
  - [x] Simple tool calls via shell or REST API
  - [x] Tool registry and permission checks
  - [x] Support for chained execution (dependent tasks)

---

### 🔍 Memory & Context Features

- [ ] Build `apps/cli/memory_viewer.py` to query stored outputs
- [ ] Enable vector store support with embedding-based context recall
- [ ] Implement contextual filtering for “related Thinklets”

---

### 🔁 Meta-Prompting Layer

- [x] Add `meta_prompting/self_reflection.py` for self-analysis
  - [x] Reflect on usefulness, tone, logical consistency
- [ ] Score meta prompts using internal rubric (chain-of-thought grading)

---

### 🧪 Evaluation System

- [ ] Expand `scorer.py` with:
  - [ ] Embedding similarity (vs. ideal answers)
  - [ ] Relevance + alignment (to prompt intent)
  - [ ] Redundancy detection

---

### 🧰 DevOps / Tooling

- [ ] Add full `pyproject.toml` for poetry/hatch + dependencies
- [ ] Add Makefile targets (`make run`, `make test`, `make zip`)
- [ ] Set up pre-commit formatting hooks (e.g., black, isort)
- [ ] Add test coverage for all core modules (`tests/unit/`)
- [ ] Add support for build tools that use the Remote Execution protocol, such as:
  - [ ] Bazel
  - [ ] Buck2
  - [ ] Goma
  - [ ] Reclient
- [ ] Add `prompt_runner.py` CLI to simulate agent execution flow
- [ ] Log agent conversations as `.md` or `.jsonl` in `logs/`
- [ ] CLI wrapper for `auto_commit_agent.py` with `--all` flag

---

## 🤖 AI-Orchestrated Development Workflows

- [ ] Implement AI-assisted multi-agent orchestration
- [ ] Define LLM-A (code generator), LLM-B (reviewer), LLM-C (synthesizer), LLM-D (supervisor)
- [ ] Chain agents using feedback and validation loops
- [ ] Enable cross-agent tool access (e.g., edit_file_tool, read_file_tool)
- [ ] Build meta_prompting/prompt_strategies.py for:
  - [ ] Minimalist Prompting
  - [ ] Modular Decomposition Prompts
  - [ ] Multi-Shot + Chain-of-Thought guidance
- [ ] Create prompt registry and evaluation system
- [ ] Track prompt ↔️ result lineage
- [ ] Score prompts by clarity, conciseness, and effectiveness
- [ ] Automate GitOps tasks via agents:
  - [ ] AI-generated commit messages, PR titles, and release notes
  - [ ] Code linting and formatting via Prettier, ESLint, Black
  - [ ] CI/CD pipeline suggestions using GitHub Actions

---

## 🧬 Future Vision

- [ ] MVP GUI/TUI with Iced.rs or Tauri (`apps/shell/`)
- [ ] Plugin system for tools / agents / scorers
- [ ] Long-term hierarchical context store (CRDT/IPFS-based)

---

## 🚀 New Feature: FAANG-Level AI Developer Mode

- [ ] Design and embed a multi-layered system prompt simulating a Principal Engineer’s discipline, tech stack, and workflows
- [ ] Create a JSON prompt template for loading as system context in AI tools
- [ ] Implement logic to load and apply the JSON system prompt in your AI call pipeline (e.g., OpenAI API, Ollama)
- [ ] Combine system prompt with task-specific user prompts for recursive file analysis, refactoring, security hardening, and CI/CD generation
- [ ] Integrate prompt-driven AI responses into existing recursive decomposition and feedback loop modules
- [ ] Persist iterative outputs for long-term project memory and meta-evaluation
- [ ] Develop test cases using Next.js/NestJS repos with sensitive config to validate the feature’s effectiveness

---

🧠 _“From prompt to system” means building infrastructure for memory, feedback, autonomy, and interaction. Stay recursive._
