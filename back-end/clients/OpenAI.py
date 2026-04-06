from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class ChatGPT:
    def __init__(self, 
        model_name: str, 
        temperature: float = 1.0, 
        max_tokens: int = 512,
    ):
        self.llm = ChatOpenAI(
            model = model_name,
            temperature = temperature,
            max_tokens = max_tokens,
        )

    def add_structured(self, format: BaseModel):
        self.llm.bind(response_format = "json_object")
        self.llm = self.llm.with_structured_output(format)

    def chat(self, prompts: list):
        return self.llm.invoke(prompts)

    def chat_batch(self, batch_prompts: list):
        return self.llm.batch(batch_prompts)
