# Defines multi-agent orchestration roles and responsibilities

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from core.context_kernel.memory_store import (
    query_memory_by_embedding,
    store_iterative_output,
    store_output,
)
from core.eval_core.scorer import OutputScorer
from core.meta_prompting.self_reflection import self_reflect
from core.tool_chain.executor import ToolExecutor
from orchestration.debugger import WorkflowDebugger


class AgentRole(str, Enum):
    CODE_GENERATOR = "LLM-A"
    REVIEWER = "LLM-B"
    SYNTHESIZER = "LLM-C"
    SUPERVISOR = "LLM-D"
    ARCHITECT = "LLM-E"  # New: System architect
    TESTER = "LLM-F"  # New: Test generator
    DOCUMENTER = "LLM-G"  # New: Documentation specialist


class AgentState(str, Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentContext:
    """Context shared between agents during orchestration."""

    session_id: str
    original_prompt: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    tool_executions: List[Dict[str, Any]] = field(default_factory=list)
    task_queue: List[Dict[str, Any]] = field(default_factory=list)
    token_budget: int = 1000000  # Simulate a token budget (e.g., 1 million tokens)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Agent:
    name: str
    role: AgentRole
    strategy: Callable[[str, AgentContext], Any]
    tools: List[str] = field(default_factory=list)  # Available tools
    permissions: List[str] = field(default_factory=list)  # Agent permissions
    state: AgentState = AgentState.IDLE
    context: Optional[AgentContext] = None

    def execute(self, prompt: str, context: AgentContext, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute agent strategy with context and tool access."""
        self.state = AgentState.EXECUTING
        self.context = context

        try:
            # Log execution start
            execution_id = str(uuid.uuid4())[:8]
            start_time = datetime.now()

            print(f"[{self.role}] Starting execution: {execution_id}")
            print(
                f"[{self.role}] Input: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
            )

            # Execute strategy with context
            result = self.strategy(prompt, context)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Create execution record
            execution_record = {
                "execution_id": execution_id,
                "parent_id": parent_id,
                "agent_role": self.role.value,
                "agent_name": self.name,
                "input": prompt,
                "output": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "state": AgentState.COMPLETED.value,
                "tools_used": self._get_tools_used(context),
                "validation_passed": True,  # Default, can be overridden
            }

            # Add to context
            context.conversation_history.append(execution_record)

            # Store in memory
            store_iterative_output(
                session_id=context.session_id,
                agent_role=self.role.value,
                prompt=prompt,
                output=result,
                parent_id=parent_id,
                reasoning=None,
            )

            self.state = AgentState.COMPLETED
            print(f"[{self.role}] Completed in {execution_time:.2f}s")

            return execution_record

        except Exception as e:
            self.state = AgentState.FAILED
            error_record = {
                "execution_id": str(uuid.uuid4())[:8],
                "parent_id": parent_id,
                "agent_role": self.role.value,
                "agent_name": self.name,
                "input": prompt,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "state": AgentState.FAILED.value,
            }
            context.conversation_history.append(error_record)
            print(f"[{self.role}] Failed: {e}")
            return error_record

    def _get_tools_used(self, context: AgentContext) -> List[str]:
        """Get list of tools used in this execution."""
        # This would track actual tool usage
        return []


class MultiAgentOrchestrator:
    """Orchestrates multi-agent development workflows."""

    def __init__(self, agents: Dict[AgentRole, Agent]):
        self.agents = agents
        self.tool_executor = ToolExecutor()
        self.scorer = OutputScorer()
        self.prompt_scorer = PromptScorer()
        self.debugger = WorkflowDebugger()
        self._setup_tools()

    def _setup_tools(self):
        """Setup tools available to agents."""
        # Register common development tools
        self.tool_executor.register_tool(
            "read_file",
            self._read_file_tool,
            "Read contents of a file",
            permissions=["read"],
        )
        self.tool_executor.register_tool(
            "write_file",
            self._write_file_tool,
            "Write content to a file",
            permissions=["write"],
        )
        self.tool_executor.register_tool(
            "search_code",
            self._search_code_tool,
            "Search for code patterns",
            permissions=["read"],
        )
        self.tool_executor.register_tool(
            "run_tests", self._run_tests_tool, "Run test suite", permissions=["execute"]
        )
        self.tool_executor.register_tool(
            "run_static_analysis",
            self._run_static_analysis_tool,
            "Run static analysis on code",
            permissions=["execute"],
        )
        self.tool_executor.register_tool(
            "run_in_sandbox",
            self._run_in_sandbox_tool,
            "Simulate running code in a secure sandbox for runtime error detection",
            permissions=["execute"],
        )

        # Conceptual: Load tools from the dynamic registry
        print("\n[Orchestrator] Loading tools from dynamic registry...")
        self.tool_executor.dynamic_registry.discover_tools(tool_paths=["plugins"]) # Example path
        for tool_name, tool_def in self.tool_executor.dynamic_registry._tools.items():
            print(f"[Orchestrator] Dynamically registered tool: {tool_name}")

    def _read_file_tool(self, filepath: str) -> str:
        """Tool to read file contents."""
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _write_file_tool(self, filepath: str, content: str) -> str:
        """Tool to write content to file."""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _search_code_tool(self, pattern: str, directory: str = ".") -> str:
        """Tool to search for code patterns."""
        import re

        results = []
        for file_path in Path(directory).rglob("*.py"):
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    if re.search(pattern, content):
                        results.append(str(file_path))
            except:
                continue
        return f"Found pattern in: {', '.join(results[:5])}"  # Limit results

    def _run_tests_tool(self, test_path: str = "tests/") -> str:
        """Tool to run tests."""
        try:
            import subprocess

            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return f"Tests completed. Exit code: {result.returncode}"
        except Exception as e:
            return f"Error running tests: {e}"

    def _run_static_analysis_tool(self, code: str) -> str:
        """Tool to simulate static analysis on code."""
        # This is a placeholder. In a real scenario, this would invoke
        # actual static analysis tools like Black, Flake8, or a security scanner.
        issues = []
        if "TODO" in code:
            issues.append("Found 'TODO' comment: Consider addressing pending tasks.")
        if "FIXME" in code:
            issues.append("Found 'FIXME' comment: Code needs immediate correction.")
        if "password" in code.lower():
            issues.append("Potential security issue: Hardcoded password found.")
        if len(code) > 1000 and code.count('\n') < 20:
            issues.append("Code complexity warning: Function might be too long or dense.")

        if issues:
            return "Static analysis found issues:\n" + "\n".join(issues)
        else:
            return "Static analysis completed: No major issues found."

    def _run_in_sandbox_tool(self, code: str) -> str:
        """Tool to simulate running code in a secure sandbox for runtime error detection."""
        # This is a placeholder for a real sandbox environment.
        # It simulates common runtime errors based on keywords in the code.
        runtime_issues = []
        if "divide by zero" in code.lower():
            runtime_issues.append("Simulated runtime error: DivisionByZeroError.")
        if "index out of bounds" in code.lower() or "list index out of range" in code.lower():
            runtime_issues.append("Simulated runtime error: IndexError.")
        if "null pointer" in code.lower() or "none object has no attribute" in code.lower():
            runtime_issues.append("Simulated runtime error: AttributeError/NullPointerException.")
        if "memory leak" in code.lower():
            runtime_issues.append("Simulated runtime warning: Potential memory leak detected.")

        if runtime_issues:
            return "Sandbox execution report: Runtime issues detected:\n" + "\n".join(runtime_issues)
        else:
            return "Sandbox execution report: No critical runtime errors detected."

    def orchestrate_development_workflow(
        self,
        user_prompt: str,
        system_prompt: str = "",
        workflow_type: str = "standard",
        enable_validation: bool = True,
        enable_feedback_loops: bool = True,
        debug_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete development workflow.

        Args:
            user_prompt: The user's development request
            system_prompt: The system prompt to use
            workflow_type: Type of workflow ("standard", "architectural", "testing", "documentation")
            enable_validation: Whether to enable validation steps
            enable_feedback_loops: Whether to enable feedback loops

        Returns:
            Complete workflow results
        """
        session_id = str(uuid.uuid4())[:8]
        context = AgentContext(session_id=session_id, original_prompt=user_prompt)
        lineage = []

        print(
            f"🚀 Starting {workflow_type} development workflow (Session: {session_id})"
        )
        print(f"📝 User Request: {user_prompt}")

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Score the initial user prompt
        prompt_score_result = self.prompt_scorer.score_prompt(user_prompt)

        workflow_steps = []

        # Step 1: Architecture Planning (if applicable)
        if workflow_type in ["architectural", "standard"]:
            architect = self.agents.get(AgentRole.ARCHITECT)
            if architect:
                if debug_mode:
                    self.debugger.set_breakpoint("architecture_planning")
                    self.debugger.pause(context, "architecture_planning")
                    # Conceptual: User can now call debugger.inspect_state() or debugger.inject_guidance()
                    # For demo, we'll just resume
                    self.debugger.resume()

                print("\n🏗️  Step 1: Architecture Planning")
                result = architect.execute(full_prompt, context)
                workflow_steps.append(("architecture", result))
                lineage.append({"parent": None, "child": result["execution_id"]})


        # Step 2: Code Generation
        if debug_mode:
            self.debugger.set_breakpoint("code_generation")
            self.debugger.pause(context, "code_generation")
            self.debugger.resume()

        print("\n💻 Step 2: Code Generation")
        code_gen = self.agents[AgentRole.CODE_GENERATOR]
        code_result = code_gen.execute(full_prompt, context)
        workflow_steps.append(("code_generation", code_result))
        lineage.append({"parent": None, "child": code_result["execution_id"]})


        # Step 3: Code Review
        if debug_mode:
            self.debugger.set_breakpoint("code_review")
            self.debugger.pause(context, "code_review")
            self.debugger.resume()

        print("\n🔍 Step 3: Code Review")
        reviewer = self.agents[AgentRole.REVIEWER]
        review_result = reviewer.execute(code_result["output"], context, parent_id=code_result["execution_id"])
        workflow_steps.append(("code_review", review_result))
        lineage.append({"parent": code_result["execution_id"], "child": review_result["execution_id"]})


        # Step 4: Feedback Loop (if enabled)
        if enable_feedback_loops:
            if debug_mode:
                self.debugger.set_breakpoint("feedback_loop")
                self.debugger.pause(context, "feedback_loop")
                self.debugger.resume()

            print("\n🔄 Step 4: Feedback Loop")
            feedback_result = self._execute_feedback_loop(
                context, code_result, review_result
            )
            workflow_steps.append(("feedback_loop", feedback_result))
            lineage.append({"parent": review_result["execution_id"], "child": feedback_result["execution_id"]})


        # Step 5: Test Generation
        print("\n🧪 Step 5: Test Generation")
        tester = self.agents.get(AgentRole.TESTER)
        if tester:
            if debug_mode:
                self.debugger.set_breakpoint("test_generation")
                self.debugger.pause(context, "test_generation")
                self.debugger.resume()

            test_result = tester.execute(code_result["output"], context, parent_id=code_result["execution_id"])
            workflow_steps.append(("test_generation", test_result))
            lineage.append({"parent": code_result["execution_id"], "child": test_result["execution_id"]})

            # Simulate running the generated tests
            print("\n▶️ Running generated tests...")
            test_run_output = self.tool_executor.execute_tool("run_tests", test_result["output"])
            test_run_record = {
                "execution_id": str(uuid.uuid4())[:8],
                "parent_id": test_result["execution_id"],
                "agent_role": "tool_execution",
                "agent_name": "run_tests_tool",
                "input": test_result["output"],
                "output": test_run_output,
                "timestamp": datetime.now().isoformat(),
                "state": "completed"
            }
            workflow_steps.append(("test_run", test_run_record))
            lineage.append({"parent": test_result["execution_id"], "child": test_run_record["execution_id"]})


        # Step 6: Documentation
        print("\n📚 Step 6: Documentation")
        documenter = self.agents.get(AgentRole.DOCUMENTER)
        if documenter:
            if debug_mode:
                self.debugger.set_breakpoint("documentation_generation")
                self.debugger.pause(context, "documentation_generation")
                self.debugger.resume()

            doc_result = documenter.execute(code_result["output"], context, parent_id=code_result["execution_id"])
            workflow_steps.append(("documentation", doc_result))
            lineage.append({"parent": code_result["execution_id"], "child": doc_result["execution_id"]})


        # Step 7: Synthesis
        if debug_mode:
            self.debugger.set_breakpoint("synthesis")
            self.debugger.pause(context, "synthesis")
            self.debugger.resume()

        print("\n🔗 Step 7: Synthesis")
        synthesizer = self.agents[AgentRole.SYNTHESIZER]
        synthesis_result = synthesizer.execute(
            f"Original: {user_prompt}\nCode: {code_result['output']}\nReview: {review_result['output']}",
            context,
            parent_id=review_result["execution_id"]
        )
        workflow_steps.append(("synthesis", synthesis_result))
        lineage.append({"parent": review_result["execution_id"], "child": synthesis_result["execution_id"]})


        # Step 8: Validation (if enabled)
        if enable_validation:
            if debug_mode:
                self.debugger.set_breakpoint("validation")
                self.debugger.pause(context, "validation")
                self.debugger.resume()

            print("\n✅ Step 8: Validation")
            validation_result = self._execute_validation(context, workflow_steps)
            workflow_steps.append(("validation", validation_result))
            lineage.append({"parent": synthesis_result["execution_id"], "child": validation_result.get("execution_id")})


        # Step 9: Supervision/Meta-evaluation
        if debug_mode:
            self.debugger.set_breakpoint("supervision")
            self.debugger.pause(context, "supervision")
            self.debugger.resume()

        print("\n🎯 Step 9: Meta-evaluation")
        supervisor = self.agents[AgentRole.SUPERVISOR]
        supervision_result = supervisor.execute(
            f"Evaluate the complete workflow for: {user_prompt}", context, parent_id=synthesis_result["execution_id"]
        )
        workflow_steps.append(("supervision", supervision_result))
        lineage.append({"parent": synthesis_result["execution_id"], "child": supervision_result["execution_id"]})


        # Final scoring
        final_score = self.scorer.score_output(synthesis_result["output"], user_prompt)

        # Compile results
        workflow_results = {
            "session_id": session_id,
            "workflow_type": workflow_type,
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "steps": workflow_steps,
            "lineage": lineage,
            "final_output": synthesis_result["output"],
            "final_score": {
                "overall": final_score.overall_score,
                "relevance": final_score.relevance_score,
                "coherence": final_score.coherence_score,
                "completeness": final_score.completeness_score,
            },
            "context": {
                "conversation_history_length": len(context.conversation_history),
                "shared_memory_keys": list(context.shared_memory.keys()),
                "validation_passed": all(
                    step[1].get("validation_passed", True)
                    for step in workflow_steps
                    if step[0] == "validation"
                ),
                "initial_prompt_score": prompt_score_result.overall_score,
                "prompt_score_details": prompt_score_result.reasoning,
            },
        }

        print(f"\n✅ Workflow completed successfully!")
        print(f"📊 Final Score: {final_score.overall_score:.3f}")

        return workflow_results

    def _execute_feedback_loop(
        self,
        context: AgentContext,
        code_result: Dict[str, Any],
        review_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute feedback loop between code generator and reviewer."""
        feedback_iterations = []
        max_iterations = 3
        execution_id = str(uuid.uuid4())[:8]

        current_code = code_result["output"]
        current_review = review_result["output"]
        parent_id = review_result["execution_id"]

        for iteration in range(max_iterations):
            print(f"    Feedback iteration {iteration + 1}/{max_iterations}")

            # Generate improved code based on review
            code_gen = self.agents[AgentRole.CODE_GENERATOR]
            improved_code = code_gen.execute(
                f"Improve this code based on the review:\nCode: {current_code}\nReview: {current_review}",
                context,
                parent_id=parent_id
            )

            # Review the improved code
            reviewer = self.agents[AgentRole.REVIEWER]
            new_review = reviewer.execute(improved_code["output"], context, parent_id=improved_code["execution_id"])

            feedback_iterations.append(
                {
                    "iteration": iteration + 1,
                    "improved_code": improved_code,
                    "new_review": new_review,
                }
            )

            current_code = improved_code["output"]
            current_review = new_review["output"]
            parent_id = new_review["execution_id"]

            # Check if review is positive enough to stop
            if "good" in current_review.lower() or "approved" in current_review.lower():
                break

        return {
            "execution_id": execution_id,
            "feedback_iterations": feedback_iterations,
            "final_code": current_code,
            "final_review": current_review,
            "iterations_performed": len(feedback_iterations),
        }

    def _execute_validation(
        self,
        context: AgentContext,
        workflow_steps: List[tuple]
    ) -> Dict[str, Any]:
        """Execute validation of the complete workflow."""
        validation_results = []
        execution_id = str(uuid.uuid4())[:8]

        # Validate code generation
        code_step = next(
            (step for step in workflow_steps if step[0] == "code_generation"), None
        )
        if code_step:
            code_validation = self._validate_code(code_step[1]["output"])
            validation_results.append(("code_validation", code_validation))

        # Validate test generation
        test_step = next(
            (step for step in workflow_steps if step[0] == "test_generation"), None
        )
        if test_step:
            test_validation = self._validate_tests(test_step[1]["output"])
            validation_results.append(("test_validation", test_validation))

        # Validate documentation
        doc_step = next(
            (step for step in workflow_steps if step[0] == "documentation"), None
        )
        if doc_step:
            doc_validation = self._validate_documentation(doc_step[1]["output"])
            validation_results.append(("documentation_validation", doc_validation))

        return {
            "execution_id": execution_id,
            "validation_results": validation_results,
            "overall_passed": all(
                result[1].get("passed", False) for result in validation_results
            ),
        }

    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Validate generated code."""
        # Basic code validation
        validation = {"passed": True, "issues": [], "suggestions": []}

        if not code.strip():
            validation["passed"] = False
            validation["issues"].append("Empty code generated")

        if "TODO" in code:
            validation["suggestions"].append("Code contains TODO items")

        if len(code.split("\n")) < 5:
            validation["suggestions"].append("Code seems too short")

        return validation

    def _validate_tests(self, tests: str) -> Dict[str, Any]:
        """Validate generated tests."""
        validation = {"passed": True, "issues": [], "suggestions": []}

        if not tests.strip():
            validation["passed"] = False
            validation["issues"].append("No tests generated")

        if "def test_" not in tests:
            validation["issues"].append("No test functions found")

        return validation

    def _validate_documentation(self, docs: str) -> Dict[str, Any]:
        """Validate generated documentation."""
        validation = {"passed": True, "issues": [], "suggestions": []}

        if not docs.strip():
            validation["passed"] = False
            validation["issues"].append("No documentation generated")

        if len(docs.split()) < 50:
            validation["suggestions"].append("Documentation seems too brief")

        return validation


# Enhanced agent strategies with context awareness
def code_generator_strategy(prompt: str, context: AgentContext) -> str:
    """Enhanced code generator with context awareness."""
    # Check for related code in memory
    related_contexts = query_memory_by_embedding(prompt, top_k=2)

    context_info = ""
    if related_contexts:
        context_info = f"\nRelated contexts found: {len(related_contexts)}"

    return f"""# Generated Code
# Request: {prompt}
# Session: {context.session_id}
{context_info}

def example_function():
    """Example implementation based on the request."""
    try:
        # TODO: Implement actual functionality
        result = "Hello from generated code"
        # Simulate a potential error condition
        if "error" in prompt.lower():
            raise ValueError("Simulated error during execution")
        return result
    except Exception as e:
        # Log the error (in a real system, this would go to a logging framework)
        print(f"Error in example_function: {e}")
        return "Error: Could not complete task due to an internal issue."

# Secure Coding Practices:
# - Always use parameterized queries for database interactions to prevent SQL injection.
# - Ensure sensitive data is encrypted in transit (e.g., HTTPS) and at rest (e.g., AES-256).
# - Avoid hardcoding credentials; use environment variables or a secure vault.
# - Implement proper input validation and sanitization for all user-supplied data.
# - Log security-related events and monitor for suspicious activities.

# Additional helper functions can be added here
"""


def reviewer_strategy(prompt: str, context: AgentContext) -> str:
    """Enhanced reviewer with context awareness."""
    return f"""# Code Review\n# Reviewing: {prompt[:100]}...\n# Session: {context.session_id}\n\n## Review Summary\n- ✅ Code structure looks good\n- ⚠️  Missing error handling\n- 💡 Consider adding type hints\n- 📝 Add more comprehensive documentation\n\n## Specific Issues\n1. No exception handling for edge cases\n2. Missing input validation\n3. Could benefit from more descriptive variable names\n\n## Recommendations\n- Add try-catch blocks for error handling\n- Implement input validation\n- Add type hints for better code clarity\n"""


def synthesizer_strategy(prompt: str, context: AgentContext) -> str:
    """Enhanced synthesizer that combines multiple outputs."""
    return f"""# Synthesis Result\n# Combining outputs for: {prompt[:100]}...\n# Session: {context.session_id}\n\n## Integrated Solution\nBased on the code generation and review feedback, here's the synthesized solution:\n\n```python\ndef improved_function():\n    \"\"\"Improved implementation with error handling and documentation.\"\"\"\n    try:\n        # Implementation with proper error handling\n        result = process_input()\n        return result\n    except Exception as e:\n        logger.error(f"Error processing: {{e}}")\n        return None\n```\n\n## Key Improvements Made\n1. Added comprehensive error handling\n2. Improved documentation\n3. Enhanced code structure\n4. Added logging for debugging\n\n## Next Steps
- Implement unit tests
- Add integration tests
- Create documentation
- **Performance Optimization:** Identify and optimize expensive operations, consider caching layers, lazy-loading, and pagination for large datasets.
"""


def supervisor_strategy(prompt: str, context: AgentContext) -> str:
    """Enhanced supervisor for meta-evaluation."""
    return f"""# Meta-Evaluation Report\n# Evaluating workflow for: {prompt[:100]}...\n# Session: {context.session_id}\n\n## Overall Assessment\n- **Quality Score**: 8.5/10\n- **Completeness**: 9/10\n- **Maintainability**: 8/10\n- **Testability**: 7/10\n\n## Strengths\n1. Comprehensive code generation\n2. Thorough review process\n3. Good synthesis of feedback\n4. Proper error handling implemented\n\n## Areas for Improvement\n1. Could benefit from more extensive testing\n2. Documentation could be more detailed\n3. Performance considerations not fully addressed\n\n## Recommendations
- Add performance benchmarks
- Implement comprehensive test suite
- Create user documentation
- Consider security implications

## Root Cause Analysis
- Analyze the root causes of any identified issues or failures.
- Provide actionable insights to prevent recurrence.
- Identify systemic weaknesses in the workflow or generated artifacts.

## Final Verdict
✅ APPROVED - Ready for production with minor improvements
"""


def architect_strategy(prompt: str, context: AgentContext) -> str:
    """System architect strategy for high-level design."""
    return f"""# System Architecture\n# Designing solution for: {prompt[:100]}...\n# Session: {context.session_id}\n\n## Architecture Overview\n- **Pattern**: Layered Architecture\n- **Scalability**: Horizontal scaling supported\n- **Maintainability**: High with clear separation of concerns\n\n## Component Design\n1. **Data Layer**: Repository pattern for data access\n2. **Business Layer**: Service-oriented architecture\n3. **Presentation Layer**: Clean API design\n4. **Infrastructure**: Containerized deployment\n\n## Technology Stack\n- Backend: Python/FastAPI\n- Database: PostgreSQL\n- Caching: Redis\n- Monitoring: Prometheus + Grafana\n\n## Security Considerations
- Input validation at all layers
- Authentication and authorization using `shared.security.auth_rate_limit.authenticate_request` and `shared.security.auth_rate_limit.authorize_request`
- Data encryption in transit and at rest
- Rate limiting enforced using `shared.security.auth_rate_limit.apply_rate_limiting`

## Meta-Analysis and Architectural Improvements
- Evaluate the overall architectural decisions for scalability, maintainability, and security.
- Suggest improvements based on common architectural patterns and best practices.
- Analyze the impact of proposed changes on the entire system.
"""


def tester_strategy(prompt: str, context: AgentContext) -> str:
    """Test generator strategy."""
    # Simulate sandbox execution
    sandbox_report = context.tool_executor.execute_tool("run_in_sandbox", prompt)

    return f"""# Generated Tests\n# Testing: {prompt[:100]}...\n# Session: {context.session_id}\n\n```python\nimport pytest\nfrom unittest.mock import Mock, patch\n\ndef test_example_function():\n    \"\"\"Test the example function.\"\"\"\n    result = example_function()\n    assert result == "Hello from generated code"\n\ndef test_example_function_with_mock():\n    \"\"\"Test with mocked dependencies.\"\"\"\n    with patch('module.dependency') as mock_dep:\n        mock_dep.return_value = "mocked_result"\n        result = example_function()\n        assert result is not None\n\ndef test_error_handling():\n    \"\"\"Test error handling scenarios.\"\"\"\n    with pytest.raises(Exception):\n        # Test error condition\n        pass\n```\n\n## Test Coverage
- Unit tests: ✅
- Integration tests: ⚠️  (needs implementation)
- Error handling tests: ✅
- Performance tests: ❌ (not implemented)

## Sandbox Execution Report
{sandbox_report}
"""


def documenter_strategy(prompt: str, context: AgentContext) -> str:
    """Documentation specialist strategy."""
    return f"""# Documentation\n# Documenting: {prompt[:100]}...\n# Session: {context.session_id}\n\n## API Documentation\n\n### `example_function()`\nReturns a greeting message.\n\n**Returns:**\n- `str`: A greeting message\n\n**Example:**\n```python\nresult = example_function()\nprint(result)  # Output: "Hello from generated code"\n```\n\n## User Guide\nThis module provides example functionality for demonstration purposes.\n\n### Getting Started\n1. Import the module\n2. Call the example function\n3. Handle the response appropriately\n\n### Error Handling\nThe function includes proper error handling for various scenarios.\n\n## Developer Notes
- This is a generated example
- Replace with actual implementation
- Add comprehensive error handling
- Consider performance implications

## Accessibility Guidelines
- Ensure all UI elements have appropriate ARIA attributes.
- Follow WCAG guidelines for contrast, keyboard navigation, and screen reader compatibility.
- Provide alt text for all images and descriptive labels for interactive elements.
"""


# Enhanced agent instances with new roles
AGENTS = {
    AgentRole.CODE_GENERATOR: Agent(
        "Gen", AgentRole.CODE_GENERATOR, code_generator_strategy
    ),
    AgentRole.REVIEWER: Agent("Rev", AgentRole.REVIEWER, reviewer_strategy),
    AgentRole.SYNTHESIZER: Agent("Synth", AgentRole.SYNTHESIZER, synthesizer_strategy),
    AgentRole.SUPERVISOR: Agent("Super", AgentRole.SUPERVISOR, supervisor_strategy),
    AgentRole.ARCHITECT: Agent("Arch", AgentRole.ARCHITECT, architect_strategy),
    AgentRole.TESTER: Agent("Test", AgentRole.TESTER, tester_strategy),
    AgentRole.DOCUMENTER: Agent("Doc", AgentRole.DOCUMENTER, documenter_strategy),
}
