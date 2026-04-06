<<<<<<< HEAD
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
=======
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config.config import path
from config.state import ParserInput
from utils import system_util
from agents.parser import parser_agent

app = FastAPI(title="Ahoy RAG API")

UPLOADS = path.uploads
system_util.make_directory(UPLOADS)


def _get_document_id() -> str:
    return system_util.get_uuid()

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(..., description="PDF 檔案"),
    creator: str = "api",
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="請上傳 PDF 檔案")

    document_id = _get_document_id()
    dest = UPLOADS / f"{document_id}.pdf"

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"讀取檔案失敗: {e}")

    try:
        dest.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存檔案失敗: {e}")

    try:
        await parser_agent.ainvoke(ParserInput(document_ids=[document_id], creator=creator))

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"執行提取失敗: {e}",
        )

    return JSONResponse(
        status_code=200,
        content = {
            "document_id": document_id,
            "message": "PDF 已上傳並完成提取",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
