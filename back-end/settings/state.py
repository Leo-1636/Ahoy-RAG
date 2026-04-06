from typing import Literal
from pydantic import BaseModel

from settings.schemas import Document

class ParserState(BaseModel):
    mode : Literal["Fast Parse", "Deep Parse", "Fast to Deep Parse"]
    documents: list[Document]