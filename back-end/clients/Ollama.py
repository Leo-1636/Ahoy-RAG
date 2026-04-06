from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from config.config import ollama

class ChatOllama:
    def __init__(self, 
        name: str, 
        temperature: float = 1.0, 
        max_tokens: int = 512, 
        timeout: float = 30
    ):
        self.name = name
        self.model = ChatOpenAI(
            model = self.name,
            temperature = temperature,
            max_tokens = max_tokens,
            timeout = timeout,
            
            api_key = ollama.api_key,
            base_url = ollama.base_url,
        )
        
    def add_structured(self, format: BaseModel):
        self.model.bind(response_format = "json_object")
        self.model = self.model.with_structured_output(format)

    def chat(self, prompts: list):
        return self.model.invoke(prompts)

    def chat_stream(self, prompts: list):
        return self.model.stream(prompts)

    def stop(self):
        import json, subprocess
        command = {
            "model" : self.name,
            "keep_alive" : 0,
        }
        subprocess.run([
            "curl", ollama.cmds_url, 
            "-d", json.dumps(command),
        ], check=True)
        
