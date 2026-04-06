import json
import uvicorn

from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessageChunk

from config import UPLOADS_PATH
from utils import system_util
from state import AnalyzerInput, RetrieverInput

from agents.analyzer import analyzer_agent
from agents.retriever import retriever_agent

app = FastAPI()

class RetrieveRequest(BaseModel):
    user_input: str
    authority: str = "public"
    images: Optional[List[str]] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.post("/upload_doc")
async def upload_documents(files: List[UploadFile] = File(...)):
    saved_pdfs = []
    system_util.make_directory(UPLOADS_PATH)
    
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, 
                detail=f"File '{file.filename}' is not a valid PDF. Only application/pdf type is allowed."
            )

        pdf_id = system_util.get_uuid()
        pdf_path = UPLOADS_PATH / f"{pdf_id}.pdf"
        
        try:
            content = await file.read()
            with pdf_path.open("wb") as buffer:
                buffer.write(content)
            saved_pdfs.append({"id": pdf_id, "name": file.filename})
        finally:
            await file.close()

    return {"message": "Successfully uploaded", "saved_pdfs": saved_pdfs}

@app.delete("/delete_doc/{pdf_id}")
async def delete_document(pdf_id: str):
    pdf_path = UPLOADS_PATH / f"{pdf_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()
        return {"message": f"Document {pdf_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@app.post("/analyze")
async def analyze(pdf_ids: List[str] = Query(...), created_by: str = Query(...)):
    async def analyze_stream():
        inputs = AnalyzerInput(pdf_ids = pdf_ids, created_by = created_by)
        async for event in analyzer_agent.astream_events(inputs, stream_mode = ["updates", "custom"]):
            kind = event["event"]
            
            if kind == "on_chain_stream":
                chunk = event["data"].get('chunk')
                
                if isinstance(chunk, AIMessageChunk):
                    continue  
                
                if isinstance(chunk, tuple) and len(chunk) > 1:
                    content = chunk[1]
                    if isinstance(content, str):
                        yield json.dumps({"type": "thought", "chunk": content, "replace": True}) + "\n"
            
            elif kind == "on_chain_end" and event["name"] == "Analyzer Agent":
                output = event["data"].get("output")
                if output and "documents" in output:
                    yield json.dumps({"type": "result", "documents": output["documents"]}) + "\n"
                    
    return StreamingResponse(analyze_stream(), media_type="text/event-stream")


@app.post("/retrieve")
async def retrieve(request: RetrieveRequest):
    # Pass images to retriever if supported, currently just input and authority
    # If RetrieverInput supports images, we should pass them:
    # inputs = RetrieverInput(user_input=request.user_input, authority=request.authority, images=request.images)
    inputs = RetrieverInput(user_input = request.user_input, authority = request.authority)
    result = await retriever_agent.ainvoke(inputs)
    return result["messages"][-1].content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)