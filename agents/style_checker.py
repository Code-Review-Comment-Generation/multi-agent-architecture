from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools
from config.settings import Config

def create_style_checker_agent():
    """Creates and returns a style checker agent"""
    return Agent(
        name="Style Checker",
        model=OpenAIChat(id=Config.OPENAI_MODEL),
        role="Check the style of the code",
        tools=[],
        add_name_to_instructions=True,
        instructions=dedent(
            """
            You are a style checker who analyzes code for readability and best practices.
            
            Your task:
            1. Review code formatting, naming conventions, and organization
            2. Identify areas where code clarity could be improved
            3. Suggest specific changes to make the code more maintainable
            
            Focus on making the code easier to understand and maintain.
        """
        ),
    )
