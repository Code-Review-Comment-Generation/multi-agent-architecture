import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
GRAPH_PATH = "graph/logs/django/repo_graph.json"
REPO_PATH = "django"


# You can add more configuration classes if needed
class Config:
    DEBUG = DEBUG
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENAI_MODEL = OPENAI_MODEL
    GRAPH_PATH = GRAPH_PATH
    REPO_PATH = REPO_PATH
