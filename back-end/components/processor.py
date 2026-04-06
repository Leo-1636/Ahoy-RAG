from config import PATH
from utils import system, pdf_io, json_io, image_io

from settings.schemas import (
    Content, Document, 
    Node, NodeProperty,
    MainNode, MainProperty,
    PageNode, PageProperty,
    Relationship,
)
from settings.prompts import (
    document_summary_schema,
    document_extraction_schema,
    document_hierarchy_schema,
)

class DocumentProcessor:
    def __init__(self, document: Document):
        self.document = document
        self.detections = []
        self.content_list = []
        self.annotations = []

    def initialize(self):
        self.document.path = PATH.DOCUMENTS / self.document.id
        self.document.page_number = pdf_io.get_page_number(self.document.path / "original.pdf")
        
    def build(self):
        for sub_folder in ["", "pages", "images"]:
            system.make_folder(self.document.path / sub_folder)
        system.move_file(PATH.ORIGINALS / f"{self.document.id}.pdf", self.document.path / "original.pdf")

    def convert_images(self):
        pdf_io.convert_images(
            source_path = self.document.path / "original.pdf",
            target_path = self.document.path / "pages/page",
            page_number = self.document.page_number,
        )

    def add_summary(self, response: document_summary_schema):
        # 待簡化
        self.document.title = response.title
        self.document.year = response.year
        self.document.language = response.language
        self.document.summary = response.summary
        self.document.to_database = response.to_database

    def add_detection(self, results: list):
        self.detections.extend(results)

    def add_contents(self, elements: list):
        for element in elements:
            image_id = system.get_uuid()
            self.content_list.append(
                Content(
                    document_id = self.document.id,
                    page_id = self.page_id,
                    type = element[5],
                    image = image_id,
                    creator = self.document.creator,
                    access_list = self.document.access_list,
                ).model_dump()
            )
            image_io.save_image(
                path = self.document.path / "images" / f"{image_id}.png",
                image = image_io.cut_image(image = self.page, bbox = element[0:4]),
            )

    def add_annotation(self, elements: list):
        self.annotations.append(
            image_io.draw_annotation(page = self.page, elements = elements)
        )

    def load_page(self, page_id: int):
        self.page_id = page_id
        self.page = image_io.open_image(self.document.path / "pages" / f"page-{page_id:0{len(str(self.document.page_number))}d}.png")
        return self.page

    def load_pages(self, start_id: int, end_id: int):
        return [
            self.load_page(page_id)
            for page_id in range(start_id, min(end_id, self.document.page_number + 1))
        ]
    
    def load_image(self, content: dict):
        return image_io.open_image(self.document.path / "images" / f"{content['image']}.png")

    def load_content_list(self):
        self.content_list = json_io.open_json(
            path = self.document.path / "content.json",
        )

    def save_content_list(self):
        json_io.save_json(
            path = self.document.path / "content.json",
            json_list = self.content_list,
        )

    def save_annotation_pdf(self):
        image_io.save_pdf(
            path = self.document.path / "annotation.pdf",
            images = self.annotations,
        )

    def update_content(self, content_id: int, responses: document_extraction_schema):
        self.content_list[content_id]["text"] = responses.content

class DatabaseProcessor:
    def __init__(self, document: Document):
        self.document = document
        self.main_node = None
        self.page_nodes = []
        self.nodes = []
        self.relationships = []

        self.content_list = []
        self.hierarchy_list = []

    def load_content(self, content: dict):
        self.content = Content.model_validate(content)
        self.load_page(self.content.page_id)

    def create_main_node(self):
        self.main_node = MainNode(
            id = system.get_uuid(),
            label = "Document",
            properties = MainProperty(
                document_id = self.document.id,
                title = self.document.title,
                year = self.document.year,
                language = self.document.language,
                summary = self.document.summary,

                creator = self.document.creator,
                access_list = self.document.access_list,
            ).model_dump(),
        ).model_dump()

    def create_page_node(self, page_id: int):
        self.page_nodes.append(
            PageNode(
                id = system.get_uuid(),
                label = "Page",
                properties = PageProperty(
                    document_id = self.document.id,
                    page_id = page_id,
                    embeddings_image = [],
                    creator = self.document.creator,
                    access_list = self.document.access_list,
                ).model_dump(),
            ).model_dump()
        )

    def create_content_node(self):
        self.nodes.append(
            Node(
                id = system.get_uuid(),
                label = self.content.type,
                properties = NodeProperty.model_validate(self.content.model_dump()).model_dump(),
            ).model_dump()
        )

    def embed_page(self, page_id: int, vector: list):
        self.page_nodes[page_id]["properties"]["embeddings_image"] = vector

    def embed_content(self, content_id: int, text_vector: list, image_vector: list):
        self.nodes[content_id]["properties"]["embeddings_text"] = text_vector
        self.nodes[content_id]["properties"]["embeddings_image"] = image_vector

    def link_pages(self):
        for page_node in self.page_nodes:
            self.relationships.append(
                Relationship(
                    start_node_id = self.main_node["id"],
                    end_node_id = page_node["id"],
                    type = "PART_OF",
                    properties = {},
                ).model_dump()
            )

    def link_sequence(self):
        if len(self.nodes) < 2:
            return
        self.relationships.append(
            Relationship(
                start_node_id = self.nodes[-2]["id"],
                end_node_id = self.nodes[-1]["id"],
                type = "NEXT",
                properties = {},
            ).model_dump()
        )

    def link_hierarchy(self):
        if len(self.hierarchy_list) < 2:
            return
        nodes_id = {
            node["properties"]["text"] : node["id"]
            for node in self.nodes
        }
        self.relationships.append(
            Relationship(
                start_node_id = nodes_id.get(self.hierarchy_list[-2]["content"]),
                end_node_id = nodes_id.get(self.hierarchy_list[-1]["content"]),
                type = "CONTAINS",
                properties = {},
            ).model_dump()
        )
        
    def load_page(self, page_id: int):
        self.page_id = page_id
        self.page = image_io.open_image(self.document.path / "pages" / f"page-{page_id:0{len(str(self.document.page_number))}d}.png")
        return self.page

    def load_pages(self, start_id: int, end_id: int):
        return [
            self.load_page(page_id)
            for page_id in range(start_id, min(end_id, self.document.page_number + 1))
        ]

    def load_content_list(self):
        self.content_list = json_io.open_json(
            path = self.document.path / "content.json",
        )

    def load_page_nodes(self):
        self.page_nodes = json_io.open_json(
            path = self.document.path / "pages.json",
        )

    def load_nodes(self):
        self.nodes = json_io.open_json(
            path = self.document.path / "nodes.json",
        )

    def load_text(self, batch_index: int, batch_size: int):
        return [node["properties"]["text"] for node in self.nodes[batch_index : batch_index + batch_size]]

    def load_image(self, batch_index: int, batch_size: int):
        return [node["properties"]["image"] for node in self.nodes[batch_index : batch_index + batch_size]]

    def load_relationships(self):
        self.relationships = json_io.open_json(
            path = self.document.path / "relationships.json",
        )
    
    def update_hierarchy(self, response: document_hierarchy_schema):
        level = response.hierarchy_level
        self.hierarchy_list = [
            item for item in self.hierarchy_list if item["level"] < level
        ] + [{"level": level, "content": self.content}]

    def save_pages(self):
        self.page_nodes = [self.main_node] + self.page_nodes
        json_io.save_json(
            path = self.document.path / "pages.json",
            json_list = self.page_nodes,
        )

    def save_nodes(self):
        json_io.save_json(
            path = self.document.path / "nodes.json",
            json_list = self.nodes,
        )

    def save_relationships(self):
        json_io.save_json(
            path = self.document.path / "relationships.json",
            json_list = self.relationships,
        )
