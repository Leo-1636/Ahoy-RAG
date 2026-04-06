import torch

from PIL.Image import Image
from sentence_transformers import SentenceTransformer

class ChatEmbedder:
    def __init__(
        self, 
        model_name: str, 
        device: str = "cuda", # "cpu" or "cuda"
        dimension: int = 256, 
        batch_size: int = 4,
    ):
        self.model = SentenceTransformer(
            model_name,
            device = device,
            trust_remote_code = True,
        )
        self.dimension = dimension
        self.batch_size = batch_size
        
    def embed_query(self, text: str):
        return self.model.encode(
            sentences = [text], 
            task = "retrieval",
            truncate_dim = self.dimension,
        ).flatten().tolist()

    def encode_text(self, batch_text: list[str]):
        return self.model.encode(
            sentences = batch_text,
            task = "retrieval",
            prompt_name = "passage",
            truncate_dim = self.dimension,
        ).tolist()

    def encode_image(self, batch_image: list[Image]):
        return self.model.encode(
            sentences = batch_image,
            task = "retrieval",
            truncate_dim = self.dimension,
        ).tolist()

    def close(self):
        self.model.cpu()
        torch.cuda.empty_cache()
