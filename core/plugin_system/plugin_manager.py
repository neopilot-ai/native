import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Type

# --- Plugin Interfaces ---


class AgentPlugin(ABC):
    """Abstract base class for agent plugins."""

    @abstractmethod
    def get_agent_role(self) -> str:
        """Returns the role of the agent (e.g., 'CODE_GENERATOR')."""
        pass

    @abstractmethod
    def get_agent_name(self) -> str:
        """Returns the name of the agent."""
        pass

    @abstractmethod
    def execute_strategy(self, prompt: str, context: Any) -> Any:
        """Executes the agent's strategy."""
        pass


class ToolPlugin(ABC):
    """Abstract base class for tool plugins."""

    @abstractmethod
    def get_tool_name(self) -> str:
        """Returns the name of the tool."""
        pass

    @abstractmethod
    def get_tool_description(self) -> str:
        """Returns a description of the tool."""
        pass

    @abstractmethod
    def get_tool_permissions(self) -> List[str]:
        """Returns a list of permissions required by the tool."""
        pass

    @abstractmethod
    def execute_tool(self, *args, **kwargs) -> Any:
        """Executes the tool's functionality."""
        pass


class ScorerPlugin(ABC):
    """Abstract base class for scorer plugins."""

    @abstractmethod
    def get_scorer_name(self) -> str:
        """Returns the name of the scorer."""
        pass

    @abstractmethod
    def score_output(self, output: str, prompt: str) -> float:
        """Scores the output based on the prompt."""
        pass


# --- Plugin Manager ---


class PluginManager:
    """Manages the discovery, loading, and registration of plugins."""

    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = [Path(d) for d in (plugin_dirs or [])]
        self.loaded_plugins: Dict[str, Any] = {}

    def load_plugins(self):
        """Discovers and loads plugins from specified directories."""
        print("🚀 Loading plugins...")
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.is_dir():
                print(f"Warning: Plugin directory not found: {plugin_dir}")
                continue

            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.name == "__init__.py":
                    continue

                module_name = plugin_file.stem
                spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                if spec is None or spec.loader is None:
                    print(f"Warning: Could not load spec for {plugin_file}")
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if (
                        isinstance(attribute, type)
                        and issubclass(
                            attribute, (AgentPlugin, ToolPlugin, ScorerPlugin)
                        )
                        and attribute is not AgentPlugin
                        and attribute is not ToolPlugin
                        and attribute is not ScorerPlugin
                    ):
                        plugin_instance = attribute()
                        self.loaded_plugins[plugin_instance.__class__.__name__] = (
                            plugin_instance
                        )
                        print(f"✅ Loaded plugin: {plugin_instance.__class__.__name__}")

    def get_plugin(self, name: str) -> Any:
        """Retrieves a loaded plugin by its class name."""
        return self.loaded_plugins.get(name)

    def get_plugins_by_type(self, plugin_type: Type[ABC]) -> Dict[str, Any]:
        """Retrieves all loaded plugins of a specific type."""
        return {
            name: plugin
            for name, plugin in self.loaded_plugins.items()
            if isinstance(plugin, plugin_type)
        }


if __name__ == "__main__":
    # Example Usage:
    # Create dummy plugin files for demonstration
    Path("plugins").mkdir(exist_ok=True)
    Path("plugins/my_agent_plugin.py").write_text(
        """
from core.plugin_system.plugin_manager import AgentPlugin

class MyAgentPlugin(AgentPlugin):
    def get_agent_role(self) -> str:
        return "CUSTOM_AGENT"

    def get_agent_name(self) -> str:
        return "My Custom Agent"

    def execute_strategy(self, prompt: str, context: Any) -> Any:
        return f"Custom agent processed: {prompt}"
"""
    )

    Path("plugins/my_tool_plugin.py").write_text(
        """
from core.plugin_system.plugin_manager import ToolPlugin

class MyToolPlugin(ToolPlugin):
    def get_tool_name(self) -> str:
        return "custom_tool"

    def get_tool_description(self) -> str:
        return "A custom tool for demonstration."

    def get_tool_permissions(self) -> List[str]:
        return ["read", "write"]

    def execute_tool(self, data: str) -> str:
        return f"Custom tool executed with: {data}"
"""
    )

    manager = PluginManager(plugin_dirs=["plugins"])
    manager.load_plugins()

    # Access loaded plugins
    agent_plugins = manager.get_plugins_by_type(AgentPlugin)
    if "MyAgentPlugin" in agent_plugins:
        custom_agent = agent_plugins["MyAgentPlugin"]
        print(
            f"\nFound Agent: {custom_agent.get_agent_name()} ({custom_agent.get_agent_role()})"
        )
        print(custom_agent.execute_strategy("Hello from main!", {}))

    tool_plugins = manager.get_plugins_by_type(ToolPlugin)
    if "MyToolPlugin" in tool_plugins:
        custom_tool = tool_plugins["MyToolPlugin"]
        print(
            f"\nFound Tool: {custom_tool.get_tool_name()} - {custom_tool.get_tool_description()}"
        )
        print(custom_tool.execute_tool("some data"))

    # Clean up dummy files
    Path("plugins/my_agent_plugin.py").unlink()
    Path("plugins/my_tool_plugin.py").unlink()
    Path("plugins").rmdir()
