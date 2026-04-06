from neo4j import AsyncGraphDatabase
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import Neo4jGraph
from neo4j_graphrag.indexes import create_vector_index

from config import Neo4j

class ChatNeo4j:
    def __init__(self):
<<<<<<< HEAD:back-end/clients/Neo4j.py
        self.driver = AsyncGraphDatabase.driver(
            url = Neo4j.BASE_URL,
            auth = Neo4j.AUTH,
=======
        self.driver = GraphDatabase.driver(
            uri = neo4j.base_url,
            auth = neo4j.auth,
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd:back-end/clients/chat_neo4j.py
        )
        self.database = neo4j.document

    async def write_graph(self, nodes: list, relationships: list):
        with self.driver as driver:
            graph = Neo4jGraph(
                nodes = nodes, 
                relationships = relationships
            )
            writer = Neo4jWriter(
                driver = driver,
<<<<<<< HEAD:back-end/clients/Neo4j.py
                neo4j_database = Neo4j.DOCUMENT,
=======
                neo4j_database = self.database,
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd:back-end/clients/chat_neo4j.py
            ).run(graph)
            await writer
            
    async def create_index(self):
        create_vector_index(
            driver = self.driver,
            name = Neo4j.TEXT_INDEX,
            label = "__Entity__",
            embedding_property = "embeddings",
            dimensions = 128,
            similarity_fn = "cosine",
<<<<<<< HEAD:back-end/clients/Neo4j.py
            neo4j_database = Neo4j.DOCUMENT,
=======
            neo4j_database = self.database,
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd:back-end/clients/chat_neo4j.py
        )
        create_vector_index(
            driver = self.driver,
            name = Neo4j.IMAGE_INDEX,
            label = "__Entity__",
            embedding_property = "embeddings_image",
            dimensions = 128,
            similarity_fn = "cosine",
<<<<<<< HEAD:back-end/clients/Neo4j.py
            neo4j_database = Neo4j.DOCUMENT,
=======
            neo4j_database = self.database,
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd:back-end/clients/chat_neo4j.py
        )

    def close(self):
        self.driver.close()
