from neo4j import AsyncGraphDatabase
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import Neo4jGraph
from neo4j_graphrag.indexes import create_vector_index

from config import Neo4j

class ChatNeo4j:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            url = Neo4j.BASE_URL,
            auth = Neo4j.AUTH,
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
                neo4j_database = Neo4j.DOCUMENT,
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
            neo4j_database = Neo4j.DOCUMENT,
        )
        create_vector_index(
            driver = self.driver,
            name = Neo4j.IMAGE_INDEX,
            label = "__Entity__",
            embedding_property = "embeddings_image",
            dimensions = 128,
            similarity_fn = "cosine",
            neo4j_database = Neo4j.DOCUMENT,
        )

    def close(self):
        self.driver.close()
