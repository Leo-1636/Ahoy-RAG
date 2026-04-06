from pathlib import Path
from pydantic import BaseModel, Field

class Document(BaseModel):
    id: str = Field(default = "")
    path: Path = Field(default = Path(""))
    creator: str = Field(default = "")
    access_list: list[str] = Field(default = [])
    page_number: int = Field(default = 1)

    title: str = Field(default = "")
    year: int = Field(default = 0)
    language: str = Field(default = "")
    summary: str = Field(default = "")
    to_database: bool = Field(default = False)

class Content(BaseModel):
    document_id: str = Field(default = "")
    page_id: int = Field(default = 0)
    type: str = Field(default = "")
    text: str = Field(default = "<Image>")
    image: str = Field(default = "")
    creator: str = Field(default = "")
    access_list: list[str] = Field(default = [])

class MainNode(BaseModel):
    id: str = Field(default = "")
    label: str = Field(default = "")
    properties: dict = Field(default = {})

class MainProperty(BaseModel):
    document_id: str = Field(default = "")
    title: str = Field(default = "")
    year: int = Field(default = 0)
    language: str = Field(default = "")
    summary: str = Field(default = "")
    creator: str = Field(default = "")
    access_list: list[str] = Field(default = [])

class PageNode(BaseModel):
    id: str = Field(default = "")
    label: str = Field(default = "")
    properties: dict = Field(default = {})

class PageProperty(BaseModel):
    document_id: str = Field(default = "")
    page_id: int = Field(default = 0)
    embeddings_image: list[float] = Field(default = [])
    creator: str = Field(default = "")
    access_list: list[str] = Field(default = [])

class Node(BaseModel):
    id: str = Field(default = "")
    label: str = Field(default = "")
    properties: dict = Field(default = {})

class NodeProperty(BaseModel):
    document_id: str = Field(default = "")
    page_id: int = Field(default = 0)
    text: str = Field(default = "")
    image: str = Field(default = "")
    embeddings_text: list[float] = Field(default = [])
    embeddings_image: list[float] = Field(default = [])
    creator: str = Field(default = "")
    access_list: list[str] = Field(default = [])

class Relationship(BaseModel):
    start_node_id: str = Field(default = "")
    end_node_id: str = Field(default = "")
    type: str = Field(default = "")
    properties: dict = Field(default = {})
