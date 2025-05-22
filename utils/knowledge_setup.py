from agno.knowledge.url import UrlKnowledge
from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.lancedb import LanceDb, SearchType


def create_knowledge_tools(urls=None, recreate=False):
    """
    Creates and returns knowledge tools with the specified URLs

    Args:
        urls (list): List of URLs to load as knowledge
        recreate (bool): Whether to recreate the knowledge base

    Returns:
        KnowledgeTools: Configured knowledge tools
    """
    if urls is None:
        urls = ["https://www.paulgraham.com/read.html"]

    # Create knowledge base
    agno_docs = UrlKnowledge(
        urls=urls,
        # Use LanceDB as the vector database
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="agno_docs",
            search_type=SearchType.hybrid,
        ),
    )

    # Load knowledge
    if recreate:
        agno_docs.load(recreate=True)

    # Create knowledge tools
    return KnowledgeTools(
        knowledge=agno_docs,
        think=True,
        search=True,
        analyze=True,
        add_few_shot=True,
    )
