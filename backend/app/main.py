from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import aiofiles
from .summarizer import summarize, summarize_stream
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import AsyncGenerator

app = FastAPI(title="LangChain‑OpenRouter Summarizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["null"] if you want to be stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextIn(BaseModel):
    text: str

@app.post("/summarize")
async def summarize_text(payload: TextIn):
    try:
        summary = await summarize(payload.text)
        return {"summary": summary}
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Summarization failed")


@app.post("/summarize-file")
async def summarize_file(txt: UploadFile = File(...)):
    if txt.content_type != "text/plain":
        raise HTTPException(status_code=415, detail="Only .txt files are supported")
    
    content = await txt.read()  # Read file contents directly
    try:
        text_content = content.decode('utf-8')  # Convert bytes to string
        summary = await summarize(text_content)
        return {"summary": summary}
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to process file")

async def stream_generator(text: str) -> AsyncGenerator[str, None]:
    try:
        async for chunk in summarize_stream(text):
            if chunk:
                yield f"data: {chunk.strip()}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
    finally:
        # Ensure cleanup
        await asyncio.sleep(0)

@app.post("/summarize-text-stream")
async def summarize_text_stream(
    background_tasks: BackgroundTasks,
    payload: TextIn
):
    return StreamingResponse(
        stream_generator(payload.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/summarize-file-stream")
async def summarize_file_stream(
    background_tasks: BackgroundTasks,
    txt: UploadFile = File(...)
):
    if txt.content_type != "text/plain":
        raise HTTPException(status_code=415, detail="Only .txt files are supported")
    
    content = await txt.read()
    text_content = content.decode('utf-8')
    
    return StreamingResponse(
        stream_generator(text_content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/summarize-stream")
async def summarize_stream_endpoint(
    background_tasks: BackgroundTasks,
    payload: TextIn
):
    async def generate():
        try:
            chunks = payload.text.split('\n\n')
            for chunk in chunks:
                if chunk.strip():
                    try:
                        summary = await summarize(chunk)
                        if summary:
                            yield f"{summary}\n"
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        yield f"Error processing chunk: {str(e)}\n"
        finally:
            # Ensure cleanup
            await asyncio.sleep(0)

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )