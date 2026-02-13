import sys
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# # Ensure `src` is on sys.path so absolute imports like `config.*` work
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import logging
from src.db.neo4j_client import Neo4jClient

log = logging.getLogger(__name__)

with Neo4jClient(load_schema=True) as client:
    result = client.run_query("RETURN 1 AS ok")
    log.info("Test query result: %s", result)

    question = "Find all customers who has a loan with PD value greater than 0.5 and return their names"

    prompt_template_d = PromptTemplate(
        input_variables=["schema", "question"],
        template=""" You generate cypher queries for the Neo4j graph database.
        Use Only Labels, properties and Relationship types as defined in the schema.
        Do not invent anything. 
        If question answer is not possible with the given schema, respond with 'Not possible'
         Schema:
        {schema} 
        Question: 
        {question}
        Cypher Query: 
        """.strip()
    )
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    cypher_query = prompt_template_d.format(schema=client.schema, question=question)
    print(f"Prompt to LLM: {cypher_query}")
    cypher = llm.invoke(cypher_query)
    print(f"Generated Cypher Query: {cypher.content}")

    customers = client.run_query(cypher.content)
    print(f"Query Result: {customers}")
    for record in customers:
        print(f"Customer: {record['c.name']}")
