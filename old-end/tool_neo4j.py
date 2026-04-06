from langchain.tools import tool

from neo4j import GraphDatabase
from neo4j_graphrag import schema
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever

from config import neo4j
from config import models
from clients.chat_embed import ChatEmbedder

embedder = ChatEmbedder(
    model_name = models.embedding_model,
    dimension = 256,
    gpu_off = True,
)

@tool
def get_schema() -> str:
    """
    Get the schema of the database.
    Returns:
        The schema of the database.
    """
    with GraphDatabase.driver(neo4j.base_url, auth = neo4j.auth) as driver:
        schema_result = schema.get_schema(
            driver = driver,
            database = neo4j.document_database,
        )
        print(f"Get Schema Result")
        return str(schema_result)

@tool
def vector_search(user_input: str, top_k: int) -> list[str]:
    """
    Search the database for the most relevant nodes based on the user input and the retrieval query.
    Args:
        user_input: The user input to search the database for.
        top_k: The number of results to return.
        filter: The filter to apply to the search.
    Returns:
        A list of the most relevant nodes in the database.
    """
    with GraphDatabase.driver(neo4j.base_url, auth = neo4j.auth) as driver:
        text_retriever = VectorRetriever(
            driver = driver,
            index_name = neo4j.text_index,
            return_properties = ["doc_id", "page_id", "text", "created_by"],
            embedder = embedder,
            neo4j_database = neo4j.document_database,
        )
        result = text_retriever.search(
            query_text = user_input, 
            top_k = top_k, 
        ).items
        print(f"Vector Search Result:")
        for item in result:
            print(f"Item: {item.content}")
        return str([item.content for item in result])

@tool
def vector_cypher_search(user_input: str, retrieval_query: str, top_k: int, filter: dict) -> list[str]:
    """
    Search the database for the most relevant nodes based on the user input and the retrieval query.
    Args:
        user_input: The user input to search the database for.
        retrieval_query: The retrieval query to use to search the database.
        top_k: The number of results to return.
        filter: The filter to apply to the search.
    Returns:
        A list of the most relevant nodes in the database.
    """
    with GraphDatabase.driver(neo4j.base_url, auth = neo4j.auth) as driver:
        text_retriever = VectorCypherRetriever(
            driver = driver,
            index_name = neo4j.text_index,
            retrieval_query = retrieval_query,
            embedder = embedder,
            neo4j_database = neo4j.document_database,
        )
        print(f"Vector Cypher Search Result:")
        result = text_retriever.search(
            query_text = user_input, 
            top_k = top_k, 
        ).items
        for item in result:
            print(f"Item: {item.content}")
        return str([item.content for item in result])
    
tools_neo4j = [get_schema, vector_search, vector_cypher_search]