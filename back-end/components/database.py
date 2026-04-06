from config.config import path
from utils import system_util, json_util, image_util

class GraphAnalyzer:
    def __init__(self, document: dict):
        self.document = document
        self.document_id = self.document['id']
        self.path = path.document / self.document_id

        self.page_nodes = []
        self.page_node_id = {}
        self.content_nodes = []
        self.relationships = []

        self.hierarchy_list = []

    def update_hierarchy(self, response, content_text: str):
        level = response.hierarchy_level
        self.hierarchy_list = [
            item for item in self.hierarchy_list if item["level"] < level
        ] + [{"level": level, "content": content_text}]

    def add_document_node(self):
        self.document_node = {
            "id": self.document_id,
            "label": "Document",
            "properties": {
                "title": self.document['title'],
                "summary": self.document['summary'],
                "language": self.document['language'],
                "created_by": self.document['creator'], 
            }
        }

    def add_page_node(self, page_id: int):
        page_node_id = system_util.get_uuid()
        self.page_nodes.append(
            {
                "id": page_node_id,
                "label": "Page",
                "properties": {
                    "document_id": self.document_id,
                    "page_id": page_id,
                    "embeddings_image": [],
                    "created_by": self.document['creator'],
                }
            }
        )
        self.relationships.append(
            {
                "start_node_id": self.document_id,
                "end_node_id": page_node_id,
                "type": "HAS_PAGE",
                "properties": {}
            }
        )
        self.page_node_id[page_id] = page_node_id

    def add_content_node(self, content: dict):
        content_node_id = system_util.get_uuid()
        self.content_nodes.append(
            {
                "id": content_node_id,
                "label": content['type'],
                "properties": {
                    "document_id": self.document_id,
                    "page_id": content['page_id'],
                    "text": content['text'],
                    "image": content['image'],
                    "embeddings": [],
                    "embeddings_image": [],
                    "created_by": self.document['creator'],
                }
            }
        )
        self.relationships.append(
            {
                "start_node_id": self.page_node_id[content['page_id']],
                "end_node_id": content_node_id,
                "type": "PART_OF",
                "properties": {}
            }
        )
    
    def add_sequence_relationship(self):
        if len(self.content_nodes) < 2:
            return
        self.relationships.append(
            {
                "start_node_id": self.content_nodes[-2]['id'],
                "end_node_id": self.content_nodes[-1]['id'],
                "type": "NEXT",
                "properties": {}
            }
        )

    def add_hierarchy_relationship(self):
        if len(self.hierarchy_list) < 2:
            return
        content_node_id = {
            node["properties"]["text"]: node["id"]
            for node in self.content_nodes
        }
        self.relationships.append(
            {
                "start_node_id": content_node_id.get(self.hierarchy_list[-2]['content']),
                "end_node_id": content_node_id.get(self.hierarchy_list[-1]['content']),
                "type": "CONTAINS",
                "properties": {}
            }
        )

    def load_nodes(self):
        return [self.document_node] + self.page_nodes + self.content_nodes

class DatabaseEmbedder:
    def __init__(self, document: dict):
        self.document_id = document['id']
        self.path = path.document / self.document_id
        self.page_number = document['page_number']

        self.nodes = json_util.open_json(
            path = self.path / "nodes.json",
        )
        self.relationships = json_util.open_json(
            path = self.path / "relationships.json",
        )

    def load_page(self, page_id: int):
        page_id = f"page-{page_id:0{len(str(self.page_number))}d}.png"
        return image_util.open_image(self.path / "pages" / page_id)

    def load_image(self, image_id: str):
        return image_util.open_image(self.path / "images" / f"{image_id}.png")

    def load_batch_page(self, page_id: int, batch_size: int):
        self.batch_nodes = self.nodes[page_id : min(page_id + batch_size, self.page_number + 1)]
        batch_page = []
        for node in self.batch_nodes:
            batch_page.append(self.load_page(node["properties"]["page_id"]))
        return batch_page

    def load_batch_content(self, batch_index: int, batch_size: int) -> tuple[list, list]:
        self.batch_nodes = self.nodes[batch_index : batch_index + batch_size]
        batch_text, batch_image = [], []
        for node in self.batch_nodes:
            batch_text.append(node["properties"]["text"])
            batch_image.append(self.load_image(node["properties"]["image"]))
        return batch_text, batch_image

    def embed_page(self, batch_vector: list):
        for node, vector in zip(self.batch_nodes, batch_vector):
            node["properties"]["embeddings_image"] = vector

    def embed_content(self, batch_text_vector: list, batch_image_vector: list):
        for node, text_vector, image_vector in zip(self.batch_nodes, batch_text_vector, batch_image_vector):
            node["properties"]["embeddings"] = text_vector
            node["properties"]["embeddings_image"] = image_vector

    def update_nodes(self):
        json_util.save_json(
            path = self.path / "nodes.json",
            json_list = self.nodes,
        )