from pathlib import Path

class PATH:
    STORAGE = Path("storage")
    ORIGINALS = STORAGE / "originals"
    DOCUMENTS = STORAGE / "documents"

class MODEL:
    reasoning_model = "Qwen/Qwen3-VL-8B-Instruct-FP8"
    embedding_model = "jinaai/jina-embeddings-v4"

    gpt5_2 = "gpt-5.2-2025-12-11"
    gpt5_nano = "gpt-5-nano-2025-08-07"
    gpt5_mini = "gpt-5-mini-2025-08-07"

class Neo4j: # 修改命名
    AUTH = ("neo4j", "password")
    BASE_URL = "neo4j://127.0.0.1:7687"

    TEXT_INDEX = "text_index"
    IMAGE_INDEX = "image_index"

    ACCOUNT = "account"
    MESSAGE = "message"
    DOCUMENT = "document"

class Ollama:
    API_KEY = "ollama"
    BASE_URL = "http://localhost:11434/v1"
    CMDS_URL = "http://localhost:11434/api/generate"

class vLLM:
    API_KEY = "EMPTY"
    BASE_URL = "http://localhost:8000/v1"
    CMDS_URL = "http://localhost:8000/"
