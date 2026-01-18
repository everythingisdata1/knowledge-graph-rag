import os

from dotenv import load_dotenv

load_dotenv()


class Neo4jConfig:
    """
    Centralized Neo4j configuration
    Loaded from environment variables
    """

    uri: str = os.getenv("NEO4J_HOST", "bolt://127.0.0.1:7687")
    user: str = os.getenv("NEO4J_USER", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "test")
    database: str = os.getenv("NEO4J_DB", "neo4j")
