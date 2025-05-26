import os
from typing import Iterator

import openai
from agno.workflow import RunResponse


def generate_github_comment(
    detailed_report: Iterator[RunResponse],
    api_key: str = None,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Generate a concise GitHub review comment from a detailed report using OpenAI API directly.

    Args:
        detailed_report: Iterator of RunResponse objects from TeamWorkflow
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        model: OpenAI model to use (default: gpt-4o-mini)

    Returns:
        str: Concise GitHub-style review comment
    """

    report_content = ""
    for response in detailed_report:
        if hasattr(response, "content") and response.content:
            report_content += response.content

    if not report_content.strip():
        return "No specific issues found in the code review analysis."

    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
        )

    client = openai.OpenAI(api_key=api_key)

    prompt = f"""Write a brief GitHub PR review comment (1-2 sentences) highlighting the top issue from this analysis:

{report_content}"""

    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Write only a concise, direct GitHub review comment. No explanations or extra text.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating GitHub comment: {str(e)}"
