import logging
import importlib
import inspect
import os
import sys
import types
import asyncio
import subprocess
import requests
from typing import Callable, Any, Dict, List, Optional

logger = logging.getLogger("ToolExecutor")
logging.basicConfig(level=logging.INFO)

class ToolExecutor:
    """
    Executes tools by name with provided arguments.
    Supports sync/async tools, error handling, logging, dynamic discovery, metadata, permissions, chaining, and shell/REST tools.
    """
    def __init__(self, user_roles: Optional[List[str]] = None):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.user_roles = user_roles or []

    def register_tool(self, name: str, func: Callable, description: str = "", permissions: Optional[List[str]] = None):
        """Register a tool by name, its callable, description, and required permissions."""
        logger.info(f"Registering tool: {name}")
        self.tools[name] = {
            "func": func,
            "description": description,
            "permissions": permissions or []
        }

    def check_permissions(self, name: str):
        """Check if the current user has permission to run the tool."""
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered.")
        required = set(tool["permissions"])
        if required and not required.intersection(self.user_roles):
            raise PermissionError(f"Insufficient permissions to run '{name}'. Required: {required}")

    def execute(self, name: str, *args, **kwargs):
        """Execute a registered tool by name with arguments (sync or async), after permission check."""
        if name not in self.tools:
            logger.error(f"Tool '{name}' is not registered.")
            raise ValueError(f"Tool '{name}' is not registered.")
        self.check_permissions(name)
        func = self.tools[name]["func"]
        try:
            if inspect.iscoroutinefunction(func):
                logger.info(f"Executing async tool: {name}")
                return asyncio.run(func(*args, **kwargs))
            else:
                logger.info(f"Executing sync tool: {name}")
                return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error executing tool '{name}': {e}")
            raise

    def execute_chain(self, tool_names: List[str], initial_input: Any = None) -> Any:
        """
        Execute a sequence of tools, passing the output of each as the input to the next.
        """
        data = initial_input
        for name in tool_names:
            if data is not None:
                data = self.execute(name, data)
            else:
                data = self.execute(name)
        return data

    def register_shell_tool(self, name: str, command_template: str, description: str = "", permissions: Optional[List[str]] = None):
        """
        Register a shell command as a tool. command_template can use {args} for positional args.
        """
        def shell_tool(*args):
            cmd = command_template.format(args=" ".join(map(str, args)))
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Shell command failed: {result.stderr}")
            return result.stdout.strip()
        self.register_tool(name, shell_tool, description, permissions)

    def register_rest_tool(self, name: str, method: str, url_template: str, description: str = "", permissions: Optional[List[str]] = None):
        """
        Register a REST API call as a tool. url_template can use {args} for positional args.
        """
        def rest_tool(*args, **kwargs):
            url = url_template.format(args="/".join(map(str, args)))
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json() if 'application/json' in resp.headers.get('Content-Type', '') else resp.text
        self.register_tool(name, rest_tool, description, permissions)

    def load_tools_from_module(self, module):
        """Register all functions in a module as tools (by function name)."""
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                self.register_tool(name, obj, description=obj.__doc__ or "")

    def load_tools_from_directory(self, directory, package=None):
        """Dynamically import all .py files in a directory and register their functions as tools."""
        sys.path.insert(0, directory)
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                modulename = filename[:-3]
                if package:
                    modulename = f"{package}.{modulename}"
                try:
                    module = importlib.import_module(modulename)
                    self.load_tools_from_module(module)
                except Exception as e:
                    logger.error(f"Failed to import {modulename}: {e}")
        sys.path.pop(0)

# Example usage
if __name__ == "__main__":
    import types
    async def async_greet(name):
        await asyncio.sleep(0.1)
        return f"Hello async, {name}!"

    def greet(name):
        return f"Hello, {name}!"

    def add(a, b):
        return a + b

    executor = ToolExecutor(user_roles=["admin"])
    executor.register_tool("greet", greet, description="Greet a user.", permissions=["user", "admin"])
    executor.register_tool("add", add, description="Add two numbers.", permissions=["admin"])
    executor.register_tool("async_greet", async_greet, description="Async greet.", permissions=["user"])
    executor.register_shell_tool("list_dir", "ls {args}", description="List directory contents.", permissions=["admin"])
    # executor.register_rest_tool("get_ip", "GET", "https://api.ipify.org?format=json", description="Get public IP.")

    print(executor.execute("greet", "Alice"))
    print(executor.execute("add", 2, 3))
    print(executor.execute("async_greet", "Bob"))
    print(executor.execute("list_dir", "."))
    print(executor.execute_chain(["greet", "async_greet"], initial_input="Chained")) 