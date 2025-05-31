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

# filepath::Class::method
# @tool(
#     name="get_function_implementation",  # Custom name for the tool
#     description="Get source code implementation of an imported function",  # Custom description
#     show_result=True,  # Show result after function call
#     stop_after_tool_call=True,  # Return result immediately after tool call
#     tool_hooks=[logger_hook],  # Hook to run before and after execution
#     # cache_results=False,  # Enable caching of results
#     # cache_dir="/tmp/agno_cache",  # Custom cache directory
#     # cache_ttl=3600,  # Cache TTL in seconds (1 hour)
# )

def get_implementation(full_qualified_name: str) -> str:
    """Get the source code implementation of a function, method or class using its fully qualified name.

    This tool helps find and retrieve the actual implementation of any code element in your codebase
    using its fully qualified name (FQN). The FQN format is: 
    for class: filepath::Class
    for method: filepath::Class::method
    for function: filepath::function

    FQN format can be gotten by seeing the import statement in the code.

    Args:
        full_qualified_name (str): The fully qualified name of the code element to find.
            Format: "filepath::Class" or "filepath::Class::method"
            Examples:
            - "tools/search_tools.py::get_implementation"
            - "graph/search.py::SearchTools::get_node_reference"
            - "config/settings.py::Config"

    Returns:
        str: The source code implementation of the requested code element from its original location.
             If the element is not found, returns an error message.

    Examples:
        # Get implementation of a standalone function
        import format: from tools.search_tools import get_implementation
        get_implementation("tools/search_tools.py::get_implementation")

        # Get implementation of a class method
        import format: from graph.search import SearchTools
        get_implementation("graph/search.py::SearchTools::get_node_reference")

        # Get implementation of a class
        import format: from config.settings import Config
        get_implementation("config/settings.py::Config")

    Notes:
        - The filepath should be relative to the project root
        - For standalone functions, use format: "filepath::function_name"
        - For class methods, use format: "filepath::Class::method"
        - For classes, use format: "filepath::Class"
    """
    print(f"Fully qualified name: {full_qualified_name}")
    node = search_tools.get_node_reference_from_fqn(full_qualified_name)

    if not node:
        print("Node not found")
        return f"Could not find implementation for '{full_qualified_name}'"

    code = search_tools.get_code_snippet(
        Config.REPO_PATH + "/" + node.loc.file_name,
        node.loc.start_line,
        node.loc.end_line,
    )
    return code