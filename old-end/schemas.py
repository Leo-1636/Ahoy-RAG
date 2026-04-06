from pydantic import BaseModel, Field

class document_summary_schema(BaseModel):
    title: str = Field(description = "The title of the document")
    summary: str = Field(description = "The summary of the document")
    language: str = Field(description = "The language of the document")
    
class document_recognition_schema(BaseModel):
    text: str = Field(description = "The text of the document content")
    
class document_hierarchy_schema(BaseModel):
    level: int = Field(description = "The hierarchical level of the document content")

class retrieval_decision_schema(BaseModel):
    status: bool = Field(description = "Whether to search the database")

class response_evaluation_schema(BaseModel):
    status: bool = Field(description = "Whether the response is satisfactory") 