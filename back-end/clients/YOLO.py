from PIL.Image import Image

from ultralytics import YOLO


class ChatYOLO:
    def __init__(self, model: str, batch_size: int = 1):
        self.model = YOLO(model)
        self.batch_size = batch_size

    async def detect(self, image: Image):
        self.result = self.model(image)[0]
        self.classes = self.result.names
        return self.result.boxes.data.tolist()

    async def detect_batch(self, images: list[Image]):
        self.results = self.model(images)
        self.classes = self.results[0].names
        return [result.boxes.data.tolist() for result in self.results]
