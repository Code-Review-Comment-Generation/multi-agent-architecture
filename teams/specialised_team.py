# from agno.models.openai import OpenAIChat
# from agno.team.team import Team


# def create_specialised_team(bug_detector_agent, style_checker_agent):
#     """Creates and returns a specialized team with the given agents"""
#     return Team(
#         name="Specialised Team",
#         mode="route",
#         model=OpenAIChat("gpt-4o"),
#         members=[
#             bug_detector_agent,
#             style_checker_agent,
#         ],
#         instructions=[
#             "You are a code review team coordinator.",
#             "Your primary role is to analyze a codebase and route the analysis to the most appropriate specialist.",
#             "For potential bugs or logical issues, route to the Bug Detector.",
#             "For code style, formatting, or best practices issues, route to the Style Checker.",
#             "Choose only one specialist based on what aspect of the code needs the most attention.",
#             "Do not attempt to reach consensus - each specialist works independently on their assigned tasks.",
#             "Your goal is to ensure the most critical issues in the codebase are identified by the right specialist.",
#         ],
#         success_criteria="The codebase has been reviewed by the right specialist.",
#         enable_agentic_context=True,
#         show_tool_calls=True,
#         markdown=True,
#         debug_mode=True,
#         show_members_responses=True,
#     )


from agno.models.openai import OpenAIChat
from agno.team.team import Team


def create_specialised_team(
    bug_detector_agent, style_checker_agent, knowledge_tools=None
):
    """
    Creates and returns a specialized team with the given agents

    Args:
        bug_detector_agent: The bug detector agent
        style_checker_agent: The style checker agent
        knowledge_tools: Optional knowledge tools to add to the team

    Returns:
        Team: The configured specialized team
    """
    # Create tools list with knowledge tools if provided
    tools = []
    if knowledge_tools:
        tools.append(knowledge_tools)

    return Team(
        name="Specialised Team",
        mode="route",
        model=OpenAIChat("gpt-4o"),
        members=[
            bug_detector_agent,
            style_checker_agent,
        ],
        tools=tools,  # Add the tools here
        instructions=[
            "You are a code review team coordinator.",
            "Your primary role is to analyze a codebase and route the analysis to the most appropriate specialist.",
            "For potential bugs or logical issues, route to the Bug Detector.",
            "For code style, formatting, or best practices issues, route to the Style Checker.",
            "Use knowledge tools to enhance your analysis when necessary.",
            "Choose only one specialist based on what aspect of the code needs the most attention.",
            "Do not attempt to reach consensus - each specialist works independently on their assigned tasks.",
            "Your goal is to ensure the most critical issues in the codebase are identified by the right specialist.",
        ],
        success_criteria="The codebase has been reviewed by the right specialist.",
        enable_agentic_context=True,
        show_tool_calls=True,
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
    )
