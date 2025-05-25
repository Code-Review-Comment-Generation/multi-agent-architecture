from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Application settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
GRAPH_PATH = 'graph/logs/sample_repo/repo_graph.json'
REPO_PATH = 'sample_repo'
# You can add more configuration classes if needed
class Config:
    DEBUG = DEBUG
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENAI_MODEL = OPENAI_MODEL
    GRAPH_PATH = GRAPH_PATH
    REPO_PATH = REPO_PATH