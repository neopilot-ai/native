import pytest

from core.tool_chain.executor import PermissionError, ToolExecutor


def greet(name):
    """Greet a user."""
    return f"Hello, {name}!"


def add(a, b):
    """Add two numbers."""
    return a + b


def test_register_and_execute():
    executor = ToolExecutor(user_roles=["admin"])
    executor.register_tool(
        "greet", greet, description="Greet a user.", permissions=["user", "admin"]
    )
    executor.register_tool(
        "add", add, description="Add two numbers.", permissions=["admin"]
    )
    assert executor.execute("greet", "Alice") == "Hello, Alice!"
    assert executor.execute("add", 2, 3) == 5


def test_permission_check():
    executor = ToolExecutor(user_roles=["user"])
    executor.register_tool(
        "add", add, description="Add two numbers.", permissions=["admin"]
    )
    with pytest.raises(PermissionError):
        executor.execute("add", 1, 2)


def test_execute_chain():
    def double(x):
        return x * 2

    def increment(x):
        return x + 1

    executor = ToolExecutor(user_roles=["admin"])
    executor.register_tool(
        "double", double, description="Double a number.", permissions=["admin"]
    )
    executor.register_tool(
        "increment", increment, description="Increment a number.", permissions=["admin"]
    )
    result = executor.execute_chain(["double", "increment"], initial_input=3)
    assert result == 7  # (3*2)+1


def test_shell_tool():
    executor = ToolExecutor(user_roles=["admin"])
    executor.register_shell_tool(
        "echo", "echo {args}", description="Echo input.", permissions=["admin"]
    )
    output = executor.execute("echo", "hello world")
    assert "hello world" in output


if __name__ == "__main__":
    test_register_and_execute()
    test_permission_check()
    test_execute_chain()
    test_shell_tool()
    print("All ToolExecutor tests passed.")
