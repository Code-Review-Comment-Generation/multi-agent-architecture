# WITHOUT KNOWLEDGE TOOLS
# import os
# from typing import Iterator

# from agno.agent import Agent, RunResponse
# from agno.utils.log import logger
# from agno.workflow import Workflow
# from dotenv import load_dotenv

# from agents import (
#     create_bug_detector_agent,
#     create_reviewer_agent,
#     create_style_checker_agent,
# )
# from teams import create_specialised_team
# from utils import fetch_codebase_content

# load_dotenv()


# class TeamWorkflow(Workflow):
#     description: str = (
#         "Review code using specialized agents to detect bugs and style issues, then format the feedback as GitHub review comments."
#     )

#     def __init__(self, debug_mode=False):
#         super().__init__(debug_mode=debug_mode)

#         # Create agents
#         self.bug_detector_agent = create_bug_detector_agent()
#         self.style_checker_agent = create_style_checker_agent()

#         # Create team
#         self.specialised_team = create_specialised_team(
#             self.bug_detector_agent, self.style_checker_agent
#         )

#         # Create reviewer agent
#         self.reviewer_agent = create_reviewer_agent()

#     def fetch_codebase_content(self, file_path="text_analyzer_demo/main.py"):
#         """
#         Fetches the content of a file to be used as the codebase for review.
#         This method wraps the utility function to allow for customization specific to this workflow.
#         """
#         return fetch_codebase_content(file_path)

#     def run(self) -> Iterator[RunResponse]:
#         logger.info(f"Getting CodeBase to review.")
#         codebase_content = self.fetch_codebase_content()

#         analysis_report: RunResponse = self.specialised_team.run(
#             f"Please review the following codebase to identify either bugs or style issues. "
#             f"Focus on the most critical problems that need addressing:\n\n```python\n{codebase_content}\n```"
#         )

#         if analysis_report is None or not analysis_report.content:
#             yield RunResponse(
#                 run_id=self.run_id, content="Sorry, could not get the analysis report."
#             )
#             return

#         logger.info("Reading the detailed analysis report and writing the comment.")
#         yield from self.reviewer_agent.run(analysis_report.content, stream=True)


# WITH KNOWLEDGE TOOLS
import os
from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.utils.log import logger
from agno.workflow import Workflow
from dotenv import load_dotenv

from agents import (
    create_bug_detector_agent,
    create_reviewer_agent,
    create_style_checker_agent,
)
from teams import create_specialised_team
from utils import create_knowledge_tools, fetch_codebase_content

load_dotenv()


class TeamWorkflow(Workflow):
    description: str = (
        "Review code using specialized agents to detect bugs and style issues, then format the feedback as GitHub review comments."
    )

    def __init__(self, debug_mode=False, recreate_knowledge=False):
        super().__init__(debug_mode=debug_mode)

        # Create agents
        self.bug_detector_agent = create_bug_detector_agent()
        self.style_checker_agent = create_style_checker_agent()

        # Create knowledge tools
        self.knowledge_tools = create_knowledge_tools(recreate=recreate_knowledge)

        # Create team with knowledge tools
        self.specialised_team = create_specialised_team(
            self.bug_detector_agent, self.style_checker_agent, self.knowledge_tools
        )

        # Create reviewer agent
        self.reviewer_agent = create_reviewer_agent()

    def fetch_codebase_content(self, file_path="text_analyzer_demo/main.py"):
        """
        Fetches the content of a file to be used as the codebase for review.
        This method wraps the utility function to allow for customization specific to this workflow.
        """
        return fetch_codebase_content(file_path)

    def run(self) -> Iterator[RunResponse]:
        logger.info(f"Getting CodeBase to review.")
        codebase_content = self.fetch_codebase_content()

        analysis_report: RunResponse = self.specialised_team.run(
            f"Please review the following codebase to identify either bugs or style issues. "
            f"Focus on the most critical problems that need addressing:\n\n```python\n{codebase_content}\n```"
        )

        if analysis_report is None or not analysis_report.content:
            yield RunResponse(
                run_id=self.run_id, content="Sorry, could not get the analysis report."
            )
            return

        logger.info("Reading the detailed analysis report and writing the comment.")
        yield from self.reviewer_agent.run(analysis_report.content, stream=True)
