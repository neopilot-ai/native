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
- [x] Add support for build tools that use the Remote Execution protocol, such as:
  - [x] Bazel
  - [x] Buck2
  - [x] Goma
  - [x] Reclient
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

## 💡 10 AI-Native Features Tailored to This Repo

1. Context-Adaptive Orchestrator (Policy Engine)

What: A policy layer that dynamically changes workflow steps, agents, or tool usage based on:
- Prompt complexity, size, domain
- Historical scores from OutputScorer / PromptScorer
- Past failure modes in conversation_history

How it fits:
- Extend MultiAgentOrchestrator.orchestrate_development_workflow to:
  - Decide workflow_type and enable_feedback_loops automatically using prompt score + memory.
  - Skip or add steps (e.g., run TESTER only if code size > N LOC; run ARCHITECT only when prompt mentions architecture/system design).

Impact: Turns your orchestrator into an adaptive AI runtime, not just a static pipeline.

2. Auto-Prompt Improvement Loop

What: A meta-agent or utility that refines the user’s prompt when PromptScorer says it’s weak, before running the main workflow.

How it fits:
- Use PromptScorer.score_prompt result in orchestrate_development_workflow:
  - If overall_score < threshold, create a meta step:
    - Ask SUPERVISOR or a new PROMPT_COACH strategy to rewrite the prompt.
  - Log both original and improved prompts in memory_store.
  - Provide a CLI flag --auto-refine-prompt.

Implementation next steps:
- [ ] Define PromptScorer threshold (start at 0.7) + configuration hook in `pyproject.toml`.
- [ ] Introduce `PROMPT_COACH` agent role + strategy file; allow SUPERVISOR fallback.
- [ ] Extend `AgentContext` with `prompt_history` storing `{original, score, refined, scorer_reasoning}` and persist via `store_output`.
- [ ] Add `--auto-refine-prompt/--no-auto-refine-prompt` flag in `apps/cli/main.py` (default off) that toggles the meta-step.
- [ ] Update CLI console output to show before/after prompt diff when refinement occurs.

Impact: Reduces garbage-in, leading to more consistent agent performance.

3. Memory-Driven Workflow Personalization

What: Personalize workflows per user/team based on past sessions:
- Preferred stack, coding style, test coverage expectations, etc.

How it fits:
- Use query_memory_by_embedding(user_prompt) in orchestrator to:
  - Detect similar past tasks and:
    - Reuse architectural patterns from ARCHITECT outputs.
    - Apply known test patterns from TESTER.
    - Bias CODE_GENERATOR prompts with “style hints”.
- Expose a CLI option --profile <name> to filter memory by profile/tenant.

Implementation next steps:
- [ ] Add `profile_id` to `AgentContext` plus CLI flag `--profile <name>` with default `default`.
- [ ] When orchestrator initializes, call `query_memory_by_embedding(user_prompt, profile_id)` and attach top results to `context.shared_memory["personalization_hints"]`.
- [ ] Define hint schema (stack, style_guidelines, testing_expectations) and ensure ARCHITECT/TESTER/CODE_GENERATOR strategies read and bias prompts accordingly.
- [ ] Persist personalization outcomes (hints applied, agent effectiveness deltas) back into memory for future weighting.

Impact: Over time, the system becomes organization-specific instead of generic.

4. Intelligent Tool Routing and Cost-Aware Planning

What: A small planner that:
- Decides which tools to call (run_tests, run_static_analysis, run_in_sandbox, custom plugins).
- Orders them based on speed, cost, and historical usefulness.

How it fits:
- Use ToolExecutor and the dynamic_registry you already have:
  - Add a plan_tools_for_step(step_name, prompt, context) policy function.
  - Track outcomes of each tool execution in context.tool_executions with success/failure/error patterns.
- Over time, build statistics in memory_store: “for codegen tasks with Python, static analysis catches more bugs than sandbox; prioritize that”.

Implementation next steps:
- [ ] Create `plan_tools_for_step(step_name, context)` helper returning ordered tool plan objects `{tool, reason, estimated_cost}`.
- [ ] Update `ToolExecutor` invocations to push execution metadata (`step`, `tool`, `duration`, `cost`, `success`, `notes`) into `context.tool_executions`.
- [ ] Extend memory store schema with `tool_stats` collection keyed by language/step to aggregate success metrics.
- [ ] Surface planner decisions in CLI debug output and add `--tool-plan=auto|manual|off` option.

Impact: Makes your system tool-aware and cost-sensitive, key for real AI-native dev workflows.

5. Self-Healing Feedback Loop (Using Eval + Memory)

What: Extend your feedback loop so it can:
- Automatically re-run only the failing steps.
- Adjust agent prompts/temperature based on evaluation feedback.

How it fits:
- In _execute_feedback_loop:
  - Incorporate OutputScorer results per iteration.
  - Store iterations_performed + scores in memory_store.
  - Auto-tune max_iterations or stopping criteria based on what historically works for that task type.

Implementation next steps:
- [ ] During `_execute_feedback_loop`, compute scorer metrics (relevance, coherence, completeness) each iteration and log in `context.validation_results`.
- [ ] Persist `{prompt, iteration, score_delta, agent_params}` records for later analysis + auto-tuning.
- [ ] Introduce adaptive stopping rule: break when `delta_overall_score < 0.02` for 2 iterations.
- [ ] Add config knobs (`max_iterations`, `min_score_gain`) to CLI `--feedback-config` JSON flag for experimentation.

Impact: System becomes self-calibrating in how aggressively it iterates.

6. Failure Pattern Mining & Auto-Guardrails

What: Automatically identify common failure patterns across sessions and turn them into guardrails.

How it fits:
- Analyze conversation_history and stored error records:
  - E.g., parse “Error reading file”, pytest failures, runtime issues hinted in sandbox strings.
- Periodically run a batch job:
  - Cluster failure messages (LLM or simple text clustering).
  - Generate:
    - “Known Pitfall” snippets (md) stored in data/ or shared/config/.
    - Proactive checks (e.g., if user asks for DB access but no environment config exists, prompt them).

Impact: Moves from reactive to proactive AI assist, preventing repeated mistakes.

7. Interactive Workflow Debugger UI (AI + Human in the Loop)

What: A simple TUI or web UI that:
- Shows each step (architecture, code, review, tests, docs, supervision).
- Lets the user edit intermediate outputs.
- Uses the existing WorkflowDebugger hooks for breakpoints.

How it fits:
- Enhance WorkflowDebugger to:
  - Serialize state snapshots into data/ or memory.
- Add a CLI mode --interactive:
  - At each breakpoint, ask the user (or another agent) whether to:
    - Continue
    - Edit the last agent output
    - Inject guidance (e.g., “use FastAPI, not Flask”)

Impact: Bridges AI automation with human oversight, improving trust.

8. Multi-Run Comparative Evaluations (A/B Agent Configs)

What: Run the same user prompt through multiple orchestrator configurations:
- Different workflow_types.
- Different prompts (FAANG vs Principal).
- Different agent strategies.

How it fits:
- Extend CLI with something like --ab-test-config <yaml> describing variants.
- Or provide a compare_workflows function:
  - Runs orchestrate_development_workflow multiple times.
  - Logs final_score and key metrics for each.
- Store results in test-results/json/ for your CI dashboard to visualize.

Impact: Treats prompting and agent design as experimentable artifacts, an AI-native design pattern.

9. Long-Term Architectural Memory + Patterns Library

What: Build a library of architectural decisions and code patterns that the ARCHITECT and CODE_GENERATOR explicitly reuse.

How it fits:
- When architect_strategy returns a good architecture (e.g., highly scored by supervisor), store a structured record:
  - Domain, stack, constraints, final architecture text.
- On new prompts, ARCHITECT checks memory for similar architectures and:
  - Starts by referencing/adapting them.
- Potentially maintain a rust/memory_fs index for fast recall in the future.

Impact: System becomes a knowledge-accumulating architect, not a stateless prompt template.

10. AI-Native CI Assistant for Remote Build Systems

What: An agent specialized in analyzing remote build/test outputs (Bazel/Buck2/Goma/Reclient) and proposing fixes.

How it fits:
- Introduce a BUILD_DOCTOR agent role:
  - Consumes JSON/JUnit outputs (like those from demo_ci_output.py and devops/remote_exec.py).
  - Uses eval signals + historical failures to:
    - Classify issue type (flaky test, missing dependency, config, infra).
    - Suggest specific fixes, config changes, or code modifications.
- Integrate into CI by:
  - Running the CLI in a GitHub Action step when failures occur.
  - Posting synthesized diagnosis + suggestions as a PR comment or CI artifact.

Impact: Makes your build & test pipeline itself AI-native, giving real value in the Fortune-50-scale build context mentioned in your README.

---

## 🧩 Phase 1 — Core Runtime & Workflows (High Priority)

Focus: Make the AI-native development loop solid, reliable, and usable end-to-end.

- [x] Foundation (MVP Milestone)
- [x] Next Objectives
  - 🔨 Core System Enhancements
  - 🛠 Tool Execution Layer
  - 🔍 Memory & Context Features
  - 🔁 Meta-Prompting Layer
  - 🧪 Evaluation System
- [x] Core items under "🤖 AI-Orchestrated Development Workflows" (multi-agent orchestration, feedback loops, prompt registry, scoring)
- [ ] From "💡 10 AI-Native Features Tailored to This Repo":
  - 3. Memory-Driven Workflow Personalization — Owner: Core Orchestration team; Blocked on AgentContext profile support; Target: Nov W4.
  - 4. Intelligent Tool Routing and Cost-Aware Planning — Owner: Tooling team; Depends on dynamic registry metrics; Target: Dec W1.

---

## 🧩 Phase 2 — DevEx, GitOps & CI (Medium Priority)

Focus: Integrate deeply with real repos, Git flows, and CI systems.

- [ ] From "🧰 DevOps / Tooling":
  - Remote Execution protocol support (Bazel, Buck2, Goma, Reclient) — Owner: DevOps Agents; Requires remote executor hardening; Target: Dec W2.
  - GitOps automation (commit messages, PR assistance, CI/CD suggestions) — Owner: GitOps squad; Needs CLI auto-commit flag telemetry; Target: Dec W3.
- [ ] From "🚀 New Feature: FAANG-Level AI Developer Mode":
  - End-to-end validation with real Next.js/NestJS test repos
- [ ] From "💡 10 AI-Native Features Tailored to This Repo":
  - 8. Multi-Run Comparative Evaluations (A/B Agent Configs) — Owner: Eval team; Blocked on PromptScorer logging upgrades; Target: Jan W1.
  - 10. AI-Native CI Assistant for Remote Build Systems — Owner: Build Doctor; Needs access to demo CI artifacts; Target: Jan W2.

---

## 🧩 Phase 3 — Long-Term Intelligence & UX (Exploratory / Long-Horizon)

Focus: Long-term memory, advanced UIs, and self-evolving behavior.

- [x] Future Vision items already implemented (GUI/TUI, plugin system, hierarchical context store, interactive workflow debugging, dynamic tool discovery, knowledge graph integration, Rust core)
- [ ] From "💡 10 AI-Native Features Tailored to This Repo":
  - 1. Context-Adaptive Orchestrator (Policy Engine) — Owner: Research; Dependency: Prompt + workload telemetry; Target: TBD (need policy DSL).
  - 2. Auto-Prompt Improvement Loop — Owner: Prompting; Kickoff once Phase 1 baseline lands; Target: TBD.
  - 5. Self-Healing Feedback Loop (Using Eval + Memory) — Owner: Eval; Requires expanded scoring data capture; Target: TBD.
  - 6. Failure Pattern Mining & Auto-Guardrails — Owner: Reliability; Needs log ingestion pipeline; Target: TBD.
  - 7. Interactive Workflow Debugger UI (AI + Human in the Loop) — Owner: UX; Depends on WorkflowDebugger snapshot API; Target: TBD.
  - 9. Long-Term Architectural Memory + Patterns Library — Owner: Architecture guild; Requires structured memory schema; Target: TBD.

---

🧠 _"From prompt to system" means building infrastructure for memory, feedback, autonomy, and interaction. Stay recursive._
