from pydantic import BaseModel, Field

class document_summary_schema(BaseModel):
    title: str = Field(description="The title of the document")
    summary: str = Field(description="The summary of the document")
    language: str = Field(description="The language of the document")
    to_database: bool = Field(
        default=False,
        description="Whether to save this document to the database",
    )

class document_extraction_schema(BaseModel):
    content: str = Field(description="The content of the document")

class document_hierarchy_schema(BaseModel):
    hierarchy_level: int = Field(description="The hierarchical level of the new content in the document")