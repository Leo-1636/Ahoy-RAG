import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from config import PATH
from utils import system
from settings.schemas import Document
from settings.state import ParserState
from agents.parser import parser_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    system.make_folder(PATH.ORIGINALS)
    uploaded = []
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code = 400, detail = f"'{file.filename}' 不是有效的 PDF 檔案")
        doc_id = system.get_uuid()
        try:
            content = await file.read()
            (PATH.ORIGINALS / f"{doc_id}.pdf").write_bytes(content)
            uploaded.append({"id": doc_id, "name": file.filename})
        finally:
            await file.close()
    return {"uploaded": uploaded}

@app.delete("/upload/{doc_id}")
async def delete_upload(doc_id: str):
    path = PATH.ORIGINALS / f"{doc_id}.pdf"
    if not path.exists():
        raise HTTPException(status_code = 404, detail = "找不到文件")
    path.unlink()
    return {"deleted": doc_id}

@app.post("/parse")
async def parse(state: ParserState):
    async def stream():
        async for message in parser_agent.astream(
            state.model_dump(mode = "json"),
            stream_mode = "custom",
        ):
            yield f"data: {message}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type = "text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 4000)
