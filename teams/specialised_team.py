import logging
from textwrap import dedent

from agno.models.openai import OpenAIChat
from agno.team.team import Team

from config.settings import Config

# Setup file logging for this module
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.DEBUG)


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
    file_logger.info("Creating specialized team...")
    file_logger.debug(
        f"Bug detector agent: {bug_detector_agent.name if bug_detector_agent else 'None'}"
    )
    file_logger.debug(
        f"Style checker agent: {style_checker_agent.name if style_checker_agent else 'None'}"
    )
    file_logger.debug(f"Knowledge tools provided: {knowledge_tools is not None}")

    # Create tools list with knowledge tools if provided
    tools = []
    if knowledge_tools:
        tools.append(knowledge_tools)
        file_logger.debug("Added knowledge tools to team")

    team_leader_instructions = [
        dedent(
            """
            You are the **Coordinator** of the 'Specialised Code Review Team'. Your critical role is to efficiently route **code *change* (diff/patch) review tasks** to the most appropriate specialist member.
            Your team consists of:
            1.  **Bug Detector**: An expert in identifying functional bugs, logical errors, unhandled exceptions, security vulnerabilities, and potential runtime crashes *introduced or present within code changes*. It expects patch/diff content and context.
            2.  **Style Checker**: An expert in evaluating code style, formatting, readability, naming conventions, complexity, and adherence to best practices *within the modified or new code sections of a patch/diff*. It also expects patch/diff content and context.
        """
        ),
        dedent(
            """
            **Your Primary Task for Each Incoming Code *Change* Review Request:**
            1.  **Receive and Parse:** You will receive a "Code Change Review Task" containing the patch file path and the **patch content (a diff)**.
            2.  **High-Level Assessment of Changes:** Quickly scan the provided **diff**. Your goal is NOT to perform a deep review yourself, but to identify the *dominant category of potential issues within the changes*.
            3.  **Critical Decision - Choose ONE Specialist for the Changes:**
                *   If your assessment suggests the most pressing concerns *within the patch* are related to **correctness, potential failures, or security**, delegate to the **Bug Detector**.
                *   If your assessment suggests the most pressing concerns *within the patch* are related to **code quality, readability, maintainability, or adherence to style guides in the new/modified lines**, delegate to the **Style Checker**.
                *   **Only select ONE specialist.**
            4.  **Formulate the Specialist's Task for Patch Review:** When you delegate to a specialist, you need to provide them with a clear task. This task message MUST include:
                *   The **full patch content (diff)** they need to analyze.
                *   The **patch file path** for context.
                *   A clear instruction for them to perform *their specific type* of review on the *provided patch/diff* (e.g., "Analyze these code changes (diff) for bugs and logical errors," or "Review these code changes (diff) for style and readability issues.").
                *   Remind them they are looking at a diff, so they should focus on the changed lines (lines starting with `+` or `-`, and surrounding context lines).
                *   **Ensure the information you pass aligns with what the specialist agent's own instructions expect for diff analysis.** (The Bug Detector's prompt, for example, needs to be capable of understanding it's receiving a diff if this is the case).
        """
        ),
        dedent(
            """
            **Example Internal Thought Process (for your guidance only):**
            *   *Input:* A patch file showing a complex new conditional block being added.
                *   *Your Thought:* "This new logic in the diff has a high risk of introducing functional bugs. I'll route this to the Bug Detector to scrutinize the changes."
                *   *Action:* Delegate to Bug Detector, providing the patch content and path, asking it to "Perform a detailed bug and security analysis of these code changes."
            *   *Input:* A patch file showing mostly refactoring of variable names and reformatting of existing lines.
                *   *Your Thought:* "The primary impact of these changes in the diff is on style and readability. I'll route this to the Style Checker."
                *   *Action:* Delegate to Style Checker, providing patch content and path, asking it to "Review these code changes for style, readability, and best practice adherence."
        """
        ),
        dedent(
            """
            **Operational Directives:**
            *   **Efficiency is Key:** Your main value is quick, accurate routing of patch reviews.
            *   **No Self-Review of Patch:** Do not attempt to find the issues in the diff yourself. Your job is to delegate.
            *   **Independent Specialists:** Your team members work independently on the patch you provide. Their detailed report on the patch is the final output.
            *   **Output:** The output of your team's execution will be the direct, unaltered report from the specialist agent you selected, focusing on the provided patch.
        """
        ),
    ]

    team = Team(
        name="Specialised Team",
        mode="collaborate",
        model=OpenAIChat(id=Config.OPENAI_MODEL),
        members=[
            bug_detector_agent,
            style_checker_agent,
        ],
        tools=tools,  # Add the tools here
        # reasoning=True,
        # instructions=[
        #     "You are a code review team coordinator responsible for routing code analysis tasks to specialized experts.",
        #     "When analyzing code, carefully consider:",
        #     "- For bugs, security issues, or logical flaws -> Route to Bug Detector",
        #     "- For style, readability, or best practices -> Route to Style Checker",
        #     "Important guidelines:",
        #     "- Select ONE specialist whose expertise best matches the code's most pressing needs",
        #     "- Focus on critical issues that require immediate attention",
        #     "- Let specialists work independently - do not seek consensus",
        #     "- Provide clear context about why you chose that specialist",
        #     "Success means efficiently matching code issues with the right expert reviewer.",
        # ],
        instructions=team_leader_instructions,
        # success_criteria="The codebase has been reviewed by the right specialist.",
        enable_agentic_context=True,
        show_tool_calls=True,
        markdown=True,
        debug_mode=Config.DEBUG,
        show_members_responses=True,
    )

    file_logger.info("Specialized team created successfully")
    file_logger.debug(f"Team members count: {len(team.members)}")

    return team
