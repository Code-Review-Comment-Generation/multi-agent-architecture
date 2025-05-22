from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools


def create_style_checker_agent():
    """Creates and returns a style checker agent"""
    return Agent(
        name="Style Checker",
        model=OpenAIChat("gpt-4o"),
        role="Check the style of the code",
        tools=[GoogleSearchTools()],
        add_name_to_instructions=True,
        instructions=dedent(
            """
            You are a style checker.
            You will be given a codebase to check the style of.
            You will need to check the style of the code.
        """
        ),
    )
