import subprocess
from typing import Any, Callable, Dict

from agno.tools import tool


def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Pre-hook function that runs before the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"{function_name} completed with.")
    return result


### pylint tool


@tool(
    name="pylint",
    description="Run pylint on the given python file",
    show_result=True,
    stop_after_tool_call=True,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600,
)
def run_pylint(file_path: str) -> str:
    """
    Run pylint on the given python file.

    Args:
        file_path (str): The path to the python file to run pylint on.

    Returns:
        str: The result of the pylint run.
    """

    pylint_output = subprocess.run(
        ["pylint", file_path], capture_output=True, text=True
    )
    return pylint_output.stdout


### flake8 tool


@tool(
    name="flake8",
    description="Run flake8 on the given python file",
    show_result=True,
    stop_after_tool_call=True,
    tool_hooks=[logger_hook],
    cache_results=True,
    cache_dir="/tmp/agno_cache",
    cache_ttl=3600,
)
def run_flake8(file_path: str) -> str:
    """
    Run flake8 on the given python file.

    Args:
        file_path (str): The path to the python file to run flake8 on.

    Returns:
        str: The result of the flake8 run.
    """

    flake8_output = subprocess.run(
        ["flake8", file_path], capture_output=True, text=True
    )
    return flake8_output.stdout


# Remove the tool decoration to call the function directly
# if __name__ == "__main__":
    # print(run_pylint("sample_repo/llm/default_plugins/openai_models.py"))
    # print(run_flake8("sample_repo/llm/default_plugins/openai_models.py"))