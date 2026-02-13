# Knowledge Graph RAG (Neo4j + LangChain)

## Objective

Build an **Graph Retrieval Augmented Generation (Graph RAG)** system using **Neo4j** and **LangChain**, enabling Large Language Models (LLMs) to generate **schema-aware Cypher queries** over a knowledge graph.

The solution ensures **accuracy, explainability, and reduced hallucination** by strictly constraining LLM outputs to the graph schema.

---

## Key Capabilities

* Schema-driven Cypher generation
* Neo4j-powered knowledge graph
* APOC-based schema introspection
* LLM-constrained querying (no invented labels/properties)
* Clean `src/`-based Python architecture

---

## Technology Stack

* **Graph Database:** Neo4j
* **Query Language:** Cypher
* **AI Framework:** LangChain
* **LLM:** OpenAI GPT-4
* **Language:** Python 3.10+
* **Plugins:** APOC
* **Build & Packaging:** setuptools, pyproject.toml

---

## Architecture (High Level)

1. Neo4j stores domain entities and relationships
2. APOC exposes schema metadata
3. LangChain injects schema + user question
4. LLM generates valid Cypher
5. Neo4j executes query and returns results

---

## Project Structure

```
graph-rag/
├── pyproject.toml
├── main.py
└── src/
    ├── config/
    └── db/
```

---

## Configuration

Environment variables:

```env
NEO4J_HOST=bolt://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=*****
NEO4J_DB=neo4j
OPENAI_API_KEY=*****
```

---

## Run

```bash
pip install -e .
python main.py
```

---

## Neo4j Requirement

APOC must be enabled:

```properties
dbms.security.procedures.unrestricted=apoc.*
dbms.security.procedures.allowlist=apoc.*
```

---

## Author

**Bharat Singh**
Java, AWS & AI Engineering Lead

---

## License

Internal / Educational Use


