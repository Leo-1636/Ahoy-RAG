from pathlib import Path

class path:
    storage = Path("storage")
    uploads = storage / "uploads"
    document = storage / "document"

class model:
    reasoning_model = "Qwen/Qwen3-VL-8B-Instruct-FP8"
    embedding_model = "jinaai/jina-embeddings-v4"

    gpt5_2 = "gpt-5.2-2025-12-11"
    gpt5_nano = "gpt-5-nano-2025-08-07"
    gpt5_mini = "gpt-5-mini-2025-08-07"

class neo4j: # 修改命名
    auth = ("neo4j", "ntousena")
    base_url = "neo4j://127.0.0.1:7687"

    text_index = "text_index"
    image_index = "image_index"

    account = "account"
    message = "message"
    document = "document"
    default = "neo4j"

class ollama:
    api_key = "ollama"
    base_url = "http://localhost:11434/v1"
    cmds_url = "http://localhost:11434/api/generate"

class vllm:
    api_key = "EMPTY"
    base_url = "http://localhost:8000/v1"
    cmds_url = "http://localhost:8000/"
