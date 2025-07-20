import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from orchestration.agent_roles import (
    AGENTS,
    AgentContext,
    AgentRole,
    AgentState,
    MultiAgentOrchestrator,
)


def test_agent_context_creation():
    """Test AgentContext creation and initialization."""
    context = AgentContext(session_id="test_session", original_prompt="Test prompt")

    assert context.session_id == "test_session"
    assert context.original_prompt == "Test prompt"
    assert len(context.conversation_history) == 0
    assert len(context.shared_memory) == 0
    assert len(context.validation_results) == 0
    assert len(context.tool_executions) == 0


def test_agent_execution():
    """Test agent execution with context."""
    agent = AGENTS[AgentRole.CODE_GENERATOR]
    context = AgentContext(session_id="test", original_prompt="Test")

    # Mock the strategy to return a predictable result
    with patch.object(agent, "strategy", return_value="Mocked code result"):
        result = agent.execute("Test prompt", context)

    assert result["agent_role"] == AgentRole.CODE_GENERATOR.value
    assert result["input"] == "Test prompt"
    assert result["output"] == "Mocked code result"
    assert result["state"] == AgentState.COMPLETED.value
    assert "execution_time" in result
    assert "timestamp" in result
    assert len(context.conversation_history) == 1


def test_agent_execution_failure():
    """Test agent execution failure handling."""
    agent = AGENTS[AgentRole.CODE_GENERATOR]
    context = AgentContext(session_id="test", original_prompt="Test")

    # Mock the strategy to raise an exception
    with patch.object(agent, "strategy", side_effect=Exception("Test error")):
        result = agent.execute("Test prompt", context)

    assert result["state"] == AgentState.FAILED.value
    assert "error" in result
    assert result["error"] == "Test error"
    assert len(context.conversation_history) == 1


def test_orchestrator_initialization():
    """Test MultiAgentOrchestrator initialization."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    assert orchestrator.agents == AGENTS
    assert orchestrator.tool_executor is not None
    assert orchestrator.scorer is not None


def test_orchestrator_tool_setup():
    """Test that orchestrator sets up tools correctly."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    # Check that tools are registered
    tools = orchestrator.tool_executor.tools
    assert "read_file" in tools
    assert "write_file" in tools
    assert "search_code" in tools
    assert "run_tests" in tools


def test_read_file_tool():
    """Test the read_file tool."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Test content")
        temp_file = f.name

    try:
        result = orchestrator._read_file_tool(temp_file)
        assert result == "Test content"
    finally:
        os.unlink(temp_file)


def test_write_file_tool():
    """Test the write_file tool."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.txt")
        content = "Test content to write"

        result = orchestrator._write_file_tool(test_file, content)

        assert "Successfully wrote" in result
        assert os.path.exists(test_file)

        with open(test_file, "r") as f:
            written_content = f.read()
            assert written_content == content


def test_search_code_tool():
    """Test the search_code tool."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("def test_function():\n    pass\n")

        result = orchestrator._search_code_tool("def test_function", temp_dir)

        assert "Found pattern in" in result
        assert "test.py" in result


def test_workflow_orchestration():
    """Test complete workflow orchestration."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    # Mock agent strategies to return predictable results
    with patch.multiple(
        AGENTS[AgentRole.CODE_GENERATOR], strategy=Mock(return_value="Generated code")
    ), patch.multiple(
        AGENTS[AgentRole.REVIEWER], strategy=Mock(return_value="Code review")
    ), patch.multiple(
        AGENTS[AgentRole.SYNTHESIZER], strategy=Mock(return_value="Synthesized result")
    ), patch.multiple(
        AGENTS[AgentRole.SUPERVISOR], strategy=Mock(return_value="Supervision result")
    ):
        results = orchestrator.orchestrate_development_workflow(
            user_prompt="Test development request",
            workflow_type="standard",
            enable_validation=False,
            enable_feedback_loops=False,
        )

    assert results["session_id"] is not None
    assert results["workflow_type"] == "standard"
    assert results["user_prompt"] == "Test development request"
    assert len(results["steps"]) > 0
    assert "final_output" in results
    assert "final_score" in results
    assert "context" in results


def test_feedback_loop_execution():
    """Test feedback loop execution."""
    orchestrator = MultiAgentOrchestrator(AGENTS)
    context = AgentContext(session_id="test", original_prompt="Test")

    code_result = {"output": "Initial code"}
    review_result = {"output": "Review with suggestions"}

    # Mock agent strategies for feedback loop
    with patch.multiple(
        AGENTS[AgentRole.CODE_GENERATOR], strategy=Mock(return_value="Improved code")
    ), patch.multiple(
        AGENTS[AgentRole.REVIEWER], strategy=Mock(return_value="Good review")
    ):
        feedback_result = orchestrator._execute_feedback_loop(
            context, code_result, review_result
        )

    assert "feedback_iterations" in feedback_result
    assert "final_code" in feedback_result
    assert "final_review" in feedback_result
    assert "iterations_performed" in feedback_result
    assert feedback_result["iterations_performed"] > 0


def test_validation_execution():
    """Test validation execution."""
    orchestrator = MultiAgentOrchestrator(AGENTS)
    context = AgentContext(session_id="test", original_prompt="Test")

    workflow_steps = [
        ("code_generation", {"output": "def test(): pass"}),
        ("test_generation", {"output": "def test_test(): pass"}),
        ("documentation", {"output": "This is documentation"}),
    ]

    validation_result = orchestrator._execute_validation(context, workflow_steps)

    assert "validation_results" in validation_result
    assert "overall_passed" in validation_result
    assert len(validation_result["validation_results"]) > 0


def test_code_validation():
    """Test code validation logic."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    # Test valid code
    valid_code = "def test_function():\n    return True"
    validation = orchestrator._validate_code(valid_code)
    assert validation["passed"] is True

    # Test empty code
    empty_code = ""
    validation = orchestrator._validate_code(empty_code)
    assert validation["passed"] is False
    assert "Empty code generated" in validation["issues"]

    # Test code with TODO
    todo_code = "def test():\n    # TODO: implement\n    pass"
    validation = orchestrator._validate_code(todo_code)
    assert validation["passed"] is True
    assert "TODO" in validation["suggestions"][0]


def test_test_validation():
    """Test test validation logic."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    # Test valid tests
    valid_tests = "def test_function():\n    assert True"
    validation = orchestrator._validate_tests(valid_tests)
    assert validation["passed"] is True

    # Test empty tests
    empty_tests = ""
    validation = orchestrator._validate_tests(empty_tests)
    assert validation["passed"] is False
    assert "No tests generated" in validation["issues"]

    # Test tests without test functions
    invalid_tests = "def not_a_test():\n    pass"
    validation = orchestrator._validate_tests(invalid_tests)
    assert validation["passed"] is False
    assert "No test functions found" in validation["issues"]


def test_documentation_validation():
    """Test documentation validation logic."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    # Test valid documentation
    valid_docs = "This is comprehensive documentation with many words to meet the minimum length requirement for validation."
    validation = orchestrator._validate_documentation(valid_docs)
    assert validation["passed"] is True

    # Test empty documentation
    empty_docs = ""
    validation = orchestrator._validate_documentation(empty_docs)
    assert validation["passed"] is False
    assert "No documentation generated" in validation["issues"]

    # Test brief documentation
    brief_docs = "Short doc"
    validation = orchestrator._validate_documentation(brief_docs)
    assert validation["passed"] is True
    assert "too brief" in validation["suggestions"][0]


def test_workflow_types():
    """Test different workflow types."""
    orchestrator = MultiAgentOrchestrator(AGENTS)

    workflow_types = ["standard", "architectural", "testing", "documentation"]

    for wf_type in workflow_types:
        with patch.multiple(
            AGENTS[AgentRole.CODE_GENERATOR],
            strategy=Mock(return_value="Generated code"),
        ), patch.multiple(
            AGENTS[AgentRole.REVIEWER], strategy=Mock(return_value="Code review")
        ), patch.multiple(
            AGENTS[AgentRole.SYNTHESIZER],
            strategy=Mock(return_value="Synthesized result"),
        ), patch.multiple(
            AGENTS[AgentRole.SUPERVISOR],
            strategy=Mock(return_value="Supervision result"),
        ):
            results = orchestrator.orchestrate_development_workflow(
                user_prompt="Test request",
                workflow_type=wf_type,
                enable_validation=False,
                enable_feedback_loops=False,
            )

            assert results["workflow_type"] == wf_type
            assert len(results["steps"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])
