from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools


def create_bug_detector_agent():
    """Creates and returns a bug detector agent"""
    return Agent(
        name="Bug Detector",
        role="Find bugs in the code",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearchTools()],
        add_name_to_instructions=True,
        instructions=dedent(
            """
        You are a bug detector.
        You will be given a codebase to research on.
        You will need to find the most relevant bugs in the codebase.
    """
        ),
    )
