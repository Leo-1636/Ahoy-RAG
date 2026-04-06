
<<<<<<< HEAD
=======
class Initializer:
    def __init__(self, id: str, creator: str):
        self.id = id
        self.creator = creator
        self.page_number = pdf_util.get_page_number(path.uploads / f"{self.id}.pdf")
        self.metadata = {
            "id": self.id,
            "creator": self.creator,
            "page_number": self.page_number
        }

    def create_storage(self):
        for sub_directory in ["", "pages", "images"]:
            system_util.make_directory(path.document / self.id / sub_directory)
        system_util.copy_file(path.uploads / f"{self.id}.pdf", path.document / self.id / "originals.pdf")
        # system_util.move_file(path.uploads / f"{self.id}.pdf", path.storage / self.id / "originals.pdf")

    def convert_images(self):
        dst_path = path.document / self.id
        pdf_util.to_images(
            src_path = dst_path / "originals.pdf",
            dst_path = dst_path / "pages/page",
            page_number = self.page_number,
        )

class Summarizer:
    def __init__(self, document: dict):
        self.document = document
        self.document_id = document["id"]
        self.page_number = document["page_number"]
        
        self.pages = []
        for page_id in range(1, min(self.page_number, 5) + 1):
            self.pages.append(image_util.open_image(path.document / self.document_id / "pages" / f"page-{page_id:0{len(str(self.page_number))}d}.png"))

    def load_metadata(self, response):
        self.metadata = response.model_dump()

    def update_metadata(self, documents: list):
        if self.metadata.get("to_database", False):
            self.document.update(self.metadata)
            documents.append(self.document)
    
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
class Persister:
    def __init__(self, document: dict):
        self.path = path.document / document["id"]
        self.title = document["title"]
        self.page_number = document["page_number"]
        self.content_list = []
        self.annotation_pdf = []

        metadata_keys = ("id", "creator", "title", "summary", "language", "page_number")
        self.metadata = {k: document[k] for k in metadata_keys}

    def load_page(self, page_id: int):
        self.page_id = page_id
        self.page = image_util.open_image(self.path / "pages" / f"page-{page_id:0{len(str(self.page_number))}d}.png")
        return self.page

    def load_image(self, content: dict):
        return image_util.open_image(self.path / "images" / f"{content['image']}.png")

    def load_content(self, content: dict):
        self.page_id = content["page_id"]
        self.content_text = content["text"]
    
    def load_content_list(self):
        self.content_list = json_util.open_json(
            path = self.path / "content.json",
        )
        return self

    def add_content_list(self, elements: list):
        self.elements = elements
        for element in self.elements:
            image_id = system_util.get_uuid()
            image_util.save_image(
                path = self.path / "images" / f"{image_id}.png",
                image = image_util.cut_image(image = self.page, bbox = element[0:4]),
            )
            self.content_list.append({
                "document_id": self.metadata["id"],
                "page_id": self.page_id,
                "type": element[5],
                "text": "<Image>",
                "image": image_id,
                "created_by": self.metadata["creator"],
            })

    def add_annotation_pdf(self):
        self.annotation_pdf.append(
            image_util.draw_page(page = self.page, elements = self.elements)
        )

    def update_content(self, content: dict, response: dict):
        content["text"] = response.content

    def update_contents(self, batch_content: list, batch_responses: list):
        for content, response in zip(batch_content, batch_responses):
            self.update_content(content, response)

    def save_content_list(self):
        json_util.save_json(
            path = self.path / "content.json",
            json_list = self.content_list,
        )

    def save_annotation_pdf(self):
        image_util.save_pdf(
            path = self.path / "annotation.pdf",
            images = self.annotation_pdf,
        )

    def save_graph_data(self, nodes: list, relationships: list):
        json_util.save_json(
            path = self.path / "nodes.json",
            json_list = nodes,
        )
        json_util.save_json(
            path = self.path / "relationships.json",
            json_list = relationships,
        )
