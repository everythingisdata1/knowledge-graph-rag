from contextlib import AbstractContextManager

from dotenv import load_dotenv

from src.config.neo4j_config import Neo4jConfig

load_dotenv()

import logging
from langchain_neo4j import Neo4jGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
log = logging.getLogger(__name__)


class Neo4jClient(AbstractContextManager):
    """
    Neo4j client wrapper for LangChain Neo4jGraph
    Handles connection lifecycle and schema loading
    """

    def __init__(self, load_schema: bool = True):
        self._graph: Neo4jGraph | None = None
        self._schema: str | None = None
        self._load_schema = load_schema
        self._config = Neo4jConfig()

    def connect(self):
        """Establish connection to Neo4j database"""
        log.info(f"Connecting to Neo4j at {self._config.uri}  DB {self._config.database}  ")
        self._graph = Neo4jGraph(
            url=self._config.uri,
            username=self._config.user,
            password=self._config.password,
            database=self._config.database
        )
        if self._load_schema:
            self._load_schema_metadata()

    def _load_schema_metadata(self):

        """Load and cache the database schema metadata"""
        log.info("Loading Neo4j schema metadata")
        try:
            self._schema = self._graph.schema
            log.info(f"Schema metadata: {self._schema}")
            log.info("Schema metadata loaded successfully")
        except Exception as e:
            log.error(f"Error loading schema metadata: {e}")
            raise

    @property
    def graph(self) -> Neo4jGraph:
        if not self._graph:
            raise RuntimeError("Neo4j client is not connected")
        return self._graph

    @property
    def schema(self) -> str | None:
        return self._schema

    def run_query(self, cypher: str, params: dict | None = None):
        """
        Execute Cypher query
        """
        return self.graph.query(cypher, params or {})

    def close(self):
        """Close the Neo4j connection"""
        log.info("Closing Neo4j connection")
        if self._graph:
            self._graph.close()
            self._graph = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __enter__(self):
        self.connect()
        return self
