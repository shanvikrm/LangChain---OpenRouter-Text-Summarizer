from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from .summarizer import summarize, summarize_stream

# ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="LangChain‑OpenRouter Summarizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # wide‑open for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Pydantic DTO ---------------------------------------------------
class TextIn(BaseModel):
    text: str

# ----- Helpers --------------------------------------------------------
async def _sse_generator(text: str):
    """
    Wrap summarize_stream() so each chunk is sent as an SSE line:  data: ...
    """
    try:
        async for chunk in summarize_stream(text):
            if chunk:
                yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as exc:
        yield f"data: Error: {exc}\n\n"
    finally:
        await asyncio.sleep(0)

# ----- Endpoints ------------------------------------------------------
@app.post("/summarize")
async def summarize_endpoint(payload: TextIn):
    """Plain JSON response with a full summary."""
    try:
        summary = await summarize(payload.text)
        return {"summary": summary}
    except Exception:
        raise HTTPException(500, "Summarization failed")

@app.post("/summarize-file")
async def summarize_file_endpoint(txt: UploadFile = File(...)):
    """Accept a .txt file and return JSON summary."""
    if txt.content_type != "text/plain":
        raise HTTPException(415, "Only .txt files are supported")
    content = (await txt.read()).decode("utf-8")
    summary = await summarize(content)
    return {"summary": summary}

@app.post("/summarize-stream")
async def summarize_stream_endpoint(payload: TextIn):
    """
    SSE stream – each yielded line starts with `data: ` so the browser
    EventSource / fetch reader can parse it.
    """
    return StreamingResponse(
        _sse_generator(payload.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
