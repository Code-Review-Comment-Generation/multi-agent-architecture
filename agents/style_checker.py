from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools
from tools.static_analysis_tool import run_pylint

from config.settings import Config


def create_style_checker_agent():
    """Creates and returns a style checker agent"""
    return Agent(
        name="Style Checker",
        model=OpenAIChat(id=Config.OPENAI_MODEL),
        # reasoning=True,
        role="Check the style of the code",
        tools=[run_pylint],
        show_tool_calls=True,
        add_name_to_instructions=True,
        debug_mode=Config.DEBUG,
        instructions=dedent(
            """
            You are a style checker who analyzes code for readability and best practices.
            
            Your task:
            1. Review code formatting, naming conventions, and organization
            2. Identify areas where code clarity could be improved
            3. Suggest specific changes to make the code more maintainable
            4. Also give the exact correct name of the files and functions where the style issue is found
            
            Focus on making the code easier to understand and maintain.
        """
        ),

    )
