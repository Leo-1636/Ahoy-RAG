import operator
from typing import TypedDict
from pydantic import BaseModel
from typing_extensions import Annotated

from langchain.messages import AnyMessage

class RetrieverInput(TypedDict):
    user_input: str
    authority: str

class RetrieverState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    images_results: Annotated[list[dict], operator.add]
    retrieval_filter: dict
    retrieval_status: bool
    evaluation_status: bool
    