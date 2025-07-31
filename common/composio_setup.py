# common/composio_tools.py

import os
from dotenv import load_dotenv
from composio_crewai import ComposioToolSet, Action

# Load environment variables
load_dotenv()

# Get API key
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")

# Initialize the Composio Toolset once
_composio_toolset = ComposioToolSet(api_key=COMPOSIO_API_KEY)

# Cache for performance
_tool_cache = {}

def get_tools_for_actions(actions: list[Action]):
    """
    Returns a list of Composio tools for the specified actions.
    Caches results for faster access in repeated calls.
    """
    key = tuple(sorted(action.name for action in actions))
    if key in _tool_cache:
        return _tool_cache[key]

    tools = _composio_toolset.get_tools(actions=actions)
    _tool_cache[key] = tools
    return tools

def get_toolset():
    """
    Returns the raw ComposioToolSet instance (for advanced use like triggers).
    """
    return _composio_toolset
