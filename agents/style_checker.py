# import logging
# from textwrap import dedent

# from agno.agent import Agent
# from agno.models.openai import OpenAIChat
# from agno.tools.googlesearch import GoogleSearchTools

# from config.settings import Config
# from tools.static_analysis_tool import run_pylint

# # Setup file logging for this module
# file_logger = logging.getLogger(__name__)
# file_logger.setLevel(logging.DEBUG)


# def create_style_checker_agent():
#     """Creates and returns a style checker agent"""
#     file_logger.info("Creating style checker agent...")

#     agent = Agent(
#         name="Style Checker",
#         model=OpenAIChat(id=Config.OPENAI_MODEL),
#         # reasoning=True,
#         role="Check the style of the code",
#         tools=[run_pylint],
#         show_tool_calls=True,
#         add_name_to_instructions=True,
#         debug_mode=Config.DEBUG,
#         instructions=dedent(
#             """
#             You are a style checker who analyzes code for readability and best practices.

#             Your task:
#             1. Review code formatting, naming conventions, and organization
#             2. Identify areas where code clarity could be improved
#             3. Suggest specific changes to make the code more maintainable
#             4. Also give the exact correct name of the files and functions where the style issue is found

#             Focus on making the code easier to understand and maintain.
#         """
#         ),
#     )

#     file_logger.info("Style checker agent created successfully")
#     file_logger.debug(f"Agent name: {agent.name}")
#     file_logger.debug(f"Debug mode: {Config.DEBUG}")

#     return agent


import logging
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools

from config.settings import Config
from tools.static_analysis_tool import run_pylint

# Setup file logging for this module
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.DEBUG)


def create_style_checker_agent():
    """Creates and returns a style checker agent"""
    file_logger.info("Creating style checker agent...")

    agent = Agent(
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
        You are a code style analysis agent. Your job is to evaluate Python source files strictly using the provided `pylint` tool.
    
        Guidelines:
        1. You MUST always use the `pylint` tool to assess a file. Do not perform manual analysis or make assumptions.
        2. When calling the tool, provide only the relative file name (e.g., 'utils.py', 'models/user.py') — the tool resolves the full path internally.
        3. After receiving the tool’s output:
           - Extract any reported issues, including the specific file and function names.
           - Explain each issue clearly and suggest actionable improvements to follow Python style and best practices.
        4. If no issues are reported, confirm that the code adheres to pylint’s style checks.
    
        You are not permitted to analyze or comment on code unless it is based entirely on the output of the `pylint` tool.
    """
        ),

    )

    file_logger.info("Style checker agent created successfully")
    file_logger.debug(f"Agent name: {agent.name}")
    file_logger.debug(f"Debug mode: {Config.DEBUG}")

    return agent
