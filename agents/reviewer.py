# import logging
# from textwrap import dedent

# from agno.agent import Agent
# from agno.models.openai import OpenAIChat
# from agno.tools.googlesearch import GoogleSearchTools

# from config.settings import Config

# # Setup file logging for this module
# file_logger = logging.getLogger(__name__)
# file_logger.setLevel(logging.DEBUG)


# def create_reviewer_agent():
#     """Creates and returns a code review comment writer agent"""
#     file_logger.info("Creating reviewer agent...")

#     agent = Agent(
#         model=OpenAIChat(id=Config.OPENAI_MODEL),
#         tools=[],
#         description="Format and finalize code review comments based on specialist analysis.",
#         instructions=[
#             "You are a code review comment writer for GitHub pull requests.",
#             "You will receive an analysis report from either a bug detector or style checker specialist.",
#             "Your task is to transform this technical analysis into clear, actionable GitHub-style review comments.",
#             "Format your review to be professional, constructive, and helpful to the developer.",
#             "Begin with a brief summary of the overall code quality.",
#             "For each issue identified in the analysis report:",
#             "   - Reference the specific file and line number",
#             "   - Explain the issue clearly and concisely",
#             "   - Suggest a specific solution or improvement",
#             "   - Provide context on why the change is recommended",
#             "If appropriate, include code snippets showing the recommended fixes.",
#             "Use Markdown formatting for better readability (code blocks, bullet points, etc.).",
#             "Prioritize the most critical issues first.",
#             "End with positive reinforcement and any overall improvement suggestions.",
#             "Keep your tone professional but friendly - focus on improving the code, not criticizing the developer.",
#         ],
#         debug_mode=Config.DEBUG,
#         show_tool_calls=True,
#         add_name_to_instructions=True,
#     )

#     file_logger.info("Reviewer agent created successfully")
#     file_logger.debug(f"Agent model: {Config.OPENAI_MODEL}")
#     file_logger.debug(f"Debug mode: {Config.DEBUG}")

#     return agent

import logging
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
# from agno.tools.googlesearch import GoogleSearchTools # Not used, can be removed

from config.settings import Config

# Setup file logging for this module
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.DEBUG)

def create_reviewer_agent():
    """Creates and returns a highly effective code review comment writer agent"""
    file_logger.info("Creating reviewer agent...")

    agent = Agent(
        model=OpenAIChat(id=Config.OPENAI_MODEL),
        tools=[],
        description="Transform technical analysis into clear, actionable, and high-impact code review comments for GitHub pull requests.",
        instructions=[
            "You are a professional code review assistant for GitHub pull requests.",
            "",
            "Your input will be a technical analysis report from tools (e.g., bug detectors, linters, or style checkers).",
            "Your task is to convert this raw analysis into clear, developer-friendly comments that can be directly used in a code review.",
            "",
            "Your goals are to:",
            "- Help the developer understand the problem quickly",
            "- Offer practical, actionable suggestions",
            "- Focus attention on high-priority or high-risk issues first",
            "- Encourage clean, maintainable, and robust code",
            "",
            "Your response should include:",
            "1. A concise summary of overall code quality and major concerns.",
            "2. A prioritized list of review comments. For each issue:",
            "   - Specify the **file name** and **line number**, if provided",
            "   - Clearly describe the issue (avoid jargon unless necessary)",
            "   - Recommend a concrete fix or code improvement",
            "   - Explain why the fix is important (e.g., readability, security, maintainability)",
            "   - Use Markdown formatting (`code`, **bold**, bullet points, etc.) for clarity",
            "   - Include example code snippets when appropriate",
            "",
            "Tone and style:",
            "- Be professional, constructive, and respectful",
            "- Avoid blame or harsh wording — treat the developer as a collaborator",
            "- Reinforce good practices where they are followed",
            "- End the review with positive encouragement or general advice",
            "",
            "Remember: your goal is not just to point out problems, but to help the developer improve the code efficiently and confidently.",
        ],
        debug_mode=Config.DEBUG,
        show_tool_calls=True,
        add_name_to_instructions=True,
    )

    file_logger.info("Reviewer agent created successfully")
    file_logger.debug(f"Agent model: {Config.OPENAI_MODEL}")
    file_logger.debug(f"Debug mode: {Config.DEBUG}")

    return agent
