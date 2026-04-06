from PIL.Image import Image
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from utils import image_io

class Message:
    def __init__(self):
        self.prompts: list[BaseMessage] = []

    def add_system(self, content: str):
        self.prompts.append(SystemMessage(content = content))

    def add_user(self, content: str | list):
        self.prompts.append(HumanMessage(content = content))

    def add_image(self, images: Image | list[Image]):
        if isinstance(images, Image):
            images = [images]
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_io.to_base64(image)}"},
            }
            for image in images
        ]
        self.prompts.append(HumanMessage(content = content))

class MessageBatch:
    def __init__(self):
        self.messages: list[list] = []

    def add(self, message: Message):
        self.messages.append(message.prompts)
        return self
