from typing import Any, Callable, Dict

from agno.tools import tool

from config.settings import Config
from graph.search import SearchTools


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Pre-hook function that runs before the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result


search_tools = SearchTools(Config.GRAPH_PATH)


@tool(
    name="get_function_implementation",  # Custom name for the tool
    description="Get source code implementation of an imported function",  # Custom description
    show_result=True,  # Show result after function call
    stop_after_tool_call=True,  # Return result immediately after tool call
    tool_hooks=[logger_hook],  # Hook to run before and after execution
    # cache_results=False,  # Enable caching of results
    # cache_dir="/tmp/agno_cache",  # Custom cache directory
    # cache_ttl=3600,  # Cache TTL in seconds (1 hour)
)
def get_function_implementation(file_path: str, function_name: str) -> str:
    """Get the source code implementation of an imported function from its original location.

    This tool helps find and retrieve the actual implementation of any imported function in your codebase.
    For example, if file A imports a function from file B, this tool will find and return
    the actual function implementation from file B.

    Args:
        file_path (str): The path of the file that imports the function (e.g. "llm/default_plugins/openai_models.py")
        function_name (str): The name of the imported function (e.g. "simplify_usage_dict")

    Returns:
        str: The source code implementation of the requested function from its original location

    Example:
        If you see an import or usage of 'simplify_usage_dict' in 'llm/default_plugins/openai_models.py',
        calling this with ("llm/default_plugins/openai_models.py", "simplify_usage_dict") will return
        its actual function implementation from wherever it was defined.
    """
    print(f"File path: {file_path}, Function name: {function_name}")
    link = search_tools.get_node_reference(file_path, function_name)

    if not link:
        print("Function link not found")
        return f"Could not find implementation for function '{function_name}'"

    node = search_tools.get_node_by_id(link.target)
    if node.type != "function":
        return f"'{function_name}' is not a function. This tool only works for function implementations."

    code = search_tools.get_code_snippet(
        Config.REPO_PATH + "/" + node.loc.file_name,
        node.loc.start_line,
        node.loc.end_line,
    )
    return code
