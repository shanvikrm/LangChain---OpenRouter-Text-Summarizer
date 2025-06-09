import os, asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

load_dotenv()  # reads .env

def _openrouter_llm(model_name: str = "meta-llama/llama-3-8b-instruct:nitro"):

    """
    Instantiate ChatOpenAI but hit the OpenRouter endpoint.
    Derived from Bryce Guinta’s adapter pattern.:contentReference[oaicite:1]{index=1}
    """
    return ChatOpenAI(
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model_name=model_name,
        temperature=0.3,
    )

# Build the summarization chain once at startup
_llm = _openrouter_llm()
_chain = load_summarize_chain(_llm, chain_type="map_reduce", return_intermediate_steps=True)

async def summarize(text: str) -> str:
    """Asynchronously return a concise summary of raw text."""
    try:
        docs = [Document(page_content=text)]
        result = await _chain.ainvoke({"input_documents": docs})
        return result.get('output_text', '').strip()
    finally:
        await asyncio.sleep(0)  # Allow event loop to clean up

async def summarize_stream(text: str):
    """Stream the summary process step by step."""
    try:
        docs = [Document(page_content=text)]
        result = await _chain.ainvoke({"input_documents": docs})
        
        # First yield intermediate steps
        if 'intermediate_steps' in result:
            for step in result['intermediate_steps']:
                yield step.strip()

        # Finally yield the output text
        if 'output_text' in result:
            yield result['output_text'].strip()
    finally:
        await asyncio.sleep(0)  # Allow event loop to clean up

