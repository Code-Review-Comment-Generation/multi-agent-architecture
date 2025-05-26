from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools

from config.settings import Config
from tools.search_tools import get_function_implementation


def create_bug_detector_agent():
    """Creates and returns a bug detector agent"""
    return Agent(
        name="Bug Detector",
        role="Find bugs in the code",
        model=OpenAIChat(id=Config.OPENAI_MODEL),
        reasoning=True,
        tools=[get_function_implementation],
        show_tool_calls=True,
        add_name_to_instructions=True,
        instructions=dedent(
            """
        You are a bug detector who analyzes code for potential issues.

        Your task:
        1. Review the code carefully to find bugs and logical errors
        2. Focus on issues that could cause the code to fail or behave incorrectly
        3. Report any bugs you find, explaining:
           - What the bug is
           - Where it occurs
           - Why it's a problem
           - How to fix it

        Tool Usage:
        - You have access to a function implementation lookup tool
        - Always use the tool `get_function_implementation` to understand how imported functions code work
        - Example: If you see `from utils import helper_func`, you can look up what helper_func does
        - func params the the fils the functions is being used in and function name
        - This helps you verify the code is using external functions correctly

        Keep your analysis focused on actual bugs rather than style issues.
    """
        ),
    )
