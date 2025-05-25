from textwrap import dedent
from tools.search_tools import get_function_implementation
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config.settings import Config

agent = Agent(
    model=OpenAIChat(id=Config.OPENAI_MODEL),
    tools=[get_function_implementation],
    instructions=dedent(
        """
        You are a code reviewer.
        You will be given a codebase to review.
        You will need to extract the implementation of all imported functions.
        """
    )
)

# Load code file
file_path = "llm/default_plugins/openai_models.py"
code_file = open(Config.REPO_PATH + "/" + file_path, "r").read()

context = f"""
From the following code, extract the implementation of all imported functions.


File Path:
{file_path}

Code:
{code_file}
"""

if __name__ == "__main__":
    agent.print_response(context, stream=True)