import subprocess
from typing import Any, Callable, Dict
import os

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
    # cache_results=True,
    # cache_dir="/tmp/agno_cache",
    # cache_ttl=3600,
)
def run_pylint(file_path: str) -> str:
    """
    Run pylint on the given python file.

    Args:
        file_path (str): The path to the python file to run pylint on.

    Returns:
        str: The result of the pylint run.
    """
    print(f"Running pylint on file: {file_path}")
    # Get the absolute path to the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get to the project root (since this script is in tools/)
    project_root = os.path.dirname(current_dir)
    # Construct the full path to the file in sample_repo
    full_file_path = os.path.join(project_root, "django", file_path)
    
    if not os.path.exists(full_file_path):
        return f"Error: File '{full_file_path}' not found. Please verify the file path and ensure the file exists in the repository."
    
    debug_file_path = os.path.join(project_root, "debug_full_file_path.txt")
    with open(debug_file_path, "w") as debug_file:
        debug_file.write(f"Input file_path: {file_path}\n")
        debug_file.write(f"Current dir: {current_dir}\n")
        debug_file.write(f"Project root: {project_root}\n")
        debug_file.write(f"Full file path: {full_file_path}\n")
        debug_file.write(f"File exists: {os.path.exists(full_file_path)}\n")
    
    try:
        # Use pylint with basic flags to focus on style issues
        pylint_output = subprocess.run(
            ["pylint", "--errors-only", "--disable=import-error", full_file_path], 
            capture_output=True, 
            text=True
        )
        
        # If no errors, run again for warnings and style issues
        if pylint_output.returncode == 0:
            pylint_output = subprocess.run(
                ["pylint", "--disable=import-error,no-name-in-module", full_file_path], 
                capture_output=True, 
                text=True
            )
        
        # Return both stdout and stderr to get complete pylint output
        output = pylint_output.stdout
        if pylint_output.stderr:
            output += f"\nSTDERR: {pylint_output.stderr}"
            
        if not output.strip():
            output = "Pylint completed successfully. No significant style issues found."
            
        return output
    except FileNotFoundError:
        return "Error: pylint command not found. Please ensure pylint is installed."
    except Exception as e:
        return f"Error running pylint: {str(e)}"


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