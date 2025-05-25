import os

from agno.utils.log import logger
from config.settings import Config

def fetch_codebase_content(file_path="text_analyzer_demo/main.py"):
    """
    Fetches the content of a file to be used as the codebase for review.

    Args:
        file_path (str): Path to the file to be fetched

    Returns:
        str: The content of the codebase to be reviewed
    """
    try:
        with open(Config.REPO_PATH + "/" + file_path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Failed to read codebase: {e}"
