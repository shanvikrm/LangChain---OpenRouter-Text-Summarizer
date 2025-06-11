"""
Central LangChain × OpenRouter summariser.

✓ Loads .env that sits **next to this file** (path‑safe)
✓ Exposes:
    • summarize(text)          → single string
    • summarize_stream(text)   → async generator (chunks)
"""

import os
import pathlib
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document


ENV_PATH = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)          # ⚠️ .env must be here

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY missing – check .env")

os.environ["OPENAI_API_KEY"] = API_KEY


def _make_llm(model: str = "meta-llama/llama-3-8b-instruct:nitro") -> ChatOpenAI:
    """Factory that returns a ChatOpenAI instance pointed at OpenRouter."""
    return ChatOpenAI(
        base_url=BASE_URL,
        openai_api_key=API_KEY,
        model_name=model,
        temperature=0.3,
    )

_llm = _make_llm()
_chain = load_summarize_chain(
    _llm,
    chain_type="map_reduce",
    return_intermediate_steps=True,
)

# ---------------------------------------------------------------------
# 3. Public helpers ----------------------------------------------------
# ---------------------------------------------------------------------
async def summarize(text: str) -> str:
    """Return a concise summary string."""
    docs = [Document(page_content=text)]
    result = await _chain.ainvoke({"input_documents": docs})
    return result.get("output_text", "").strip()

async def summarize_stream(text: str):
    """
    Async generator that yields intermediate steps then final summary,
    suitable for Server‑Sent Events (text/event‑stream).
    """
    docs = [Document(page_content=text)]
    result = await _chain.ainvoke({"input_documents": docs})

    for step in result.get("intermediate_steps", []):
        yield step.strip()
    final = result.get("output_text", "").strip()
    if final:
        yield final
    # tiny yield‑to‑loop so FastAPI streaming doesn’t stall
    await asyncio.sleep(0)
