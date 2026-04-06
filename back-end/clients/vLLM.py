import asyncio
import subprocess
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

from config import vLLM

class ChatVLLM:
    def __init__(self, 
        model_name: str, 
        temperature: float = 1.0, 
        max_tokens: int = 512, 
        batch_size: int = 1,
        timeout: float = 30,
        max_retries: int = 3,
    ):
        self.cmd = CmdVLLM(
            base_url = vLLM.CMDS_URL,
        )
        self.cmd.wake_up()
        self.model = ChatOpenAI(
            model = model_name,
            temperature = temperature,
            max_tokens = max_tokens,
            timeout = timeout,
            max_retries = max_retries,
            
            api_key = vLLM.API_KEY,
            base_url = vLLM.BASE_URL,
        )
        self.batch_size = batch_size

    def add_structured(self, schema: BaseModel):
        self.model.bind(response_format = "json_object")
        self.model = self.model.with_structured_output(schema)
        return self

    async def chat(self, prompts: list):
        return await self.model.ainvoke(prompts)

    def batch(self, batch_prompts: list):
        return self.model.batch(batch_prompts)
        
    def stream(self, prompts: list):
        for chunk in self.model.stream(prompts):
            yield chunk

    async def async_chat(self, prompts: list):
        return await self.model.ainvoke(prompts)

    async def async_batch(self, batch_prompts: list):
        return await self.model.abatch(batch_prompts)

    async def async_stream(self, prompts: list):
        async for chunk in self.model.astream(prompts):
            yield chunk

    def sleep(self, level: int = 1):
        self.cmd.sleep(level)

class CmdVLLM:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def post(self, path: str, json_body: str | None = None):
        cmd = ["curl", "-X", "POST", f"{self.base_url}{path}"]
        if json_body:
            cmd += ["-H", "Content-Type: application/json", "-d", json_body]
        subprocess.run(cmd)

    def sleep(self, level: int = 1):
        self.post(f"sleep?level={level}")

    def wake_up(self, level: int = 1):
        self.post("wake_up")    
        if level == 2:
            self.post("collective_rpc", '{"method":"reload_weights"}')
            self.post("reset_prefix_cache")
