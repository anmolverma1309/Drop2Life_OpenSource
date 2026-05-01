"""
AI Client setup.
Initialises boto3 for Titan Embeddings v2 (AWS) and httpx for Nemotron-3 (OpenRouter).
"""

import json
import asyncio
import logging
import hashlib
import math
from typing import Any

import boto3
from botocore.config import Config
import httpx
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings

logger = logging.getLogger(__name__)

# Model IDs
TITAN_EMBED_MODEL = "amazon.titan-embed-text-v2:0"


@lru_cache()
def get_bedrock_runtime():
    """Cached boto3 Bedrock Runtime client."""
    settings = get_settings()
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
        config=Config(
            retries={"max_attempts": 3, "mode": "adaptive"},
            connect_timeout=10,
            read_timeout=60,
        ),
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def _invoke_titan_embed_sync(text: str) -> list[float]:
    """Synchronous Titan Embeddings v2 call (runs in thread pool)."""
    client = get_bedrock_runtime()
    body = json.dumps({
        "inputText": text[:8000],   # Titan v2 max context
        "dimensions": 1024,
        "normalize": True,
    })
    response = client.invoke_model(
        modelId=TITAN_EMBED_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True,
)
async def _embed_text_huggingface(text: str) -> list[float]:
    """Free embeddings via Hugging Face Inference API."""
    settings = get_settings()
    endpoint = f"https://api-inference.huggingface.co/models/{settings.hf_embedding_model}"

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.hf_api_key:
        headers["Authorization"] = f"Bearer {settings.hf_api_key}"

    payload: dict[str, Any] = {
        "inputs": text[:2000],
        "options": {"wait_for_model": True},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    if isinstance(data, list) and data and isinstance(data[0], list):
        # Token-level vectors -> mean pool to a fixed-size sentence vector.
        if data and isinstance(data[0][0], (int, float)):
            dim = len(data[0])
            sums = [0.0] * dim
            for vec in data:
                if isinstance(vec, list) and len(vec) == dim:
                    for i, val in enumerate(vec):
                        sums[i] += float(val)
            count = len(data)
            if count > 0:
                return [v / count for v in sums]

        # Some providers return nested token vectors: [ [ [..], [..] ] ]
        if data and isinstance(data[0][0], list):
            nested = data[0]
            if nested and isinstance(nested[0], list):
                dim = len(nested[0])
                sums = [0.0] * dim
                count = 0
                for vec in nested:
                    if isinstance(vec, list) and len(vec) == dim:
                        for i, val in enumerate(vec):
                            sums[i] += float(val)
                        count += 1
                if count > 0:
                    return [v / count for v in sums]

    if isinstance(data, list) and data and isinstance(data[0], (int, float)):
        return [float(x) for x in data]

    raise ValueError("Unexpected Hugging Face embedding response format")


async def embed_text(text: str) -> list[float]:
    """
    Provider-aware embedding wrapper:
    - local (fully free, no API key)
    - huggingface (free) via Inference API
    - bedrock (AWS Titan v2)
    """
    settings = get_settings()
    provider = settings.embedding_provider.lower()

    if provider == "local":
        # Deterministic hashed bag-of-words embedding (dimension = 384).
        # This avoids paid providers while keeping vector search functional.
        dim = 384
        vec = [0.0] * dim
        tokens = [t for t in text.lower().split() if t]
        if not tokens:
            return vec

        for tok in tokens:
            digest = hashlib.sha256(tok.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % dim
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0)
            vec[idx] += sign * weight

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    if provider == "huggingface":
        return await _embed_text_huggingface(text)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _invoke_titan_embed_sync, text)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True,
)
async def call_claude(system_prompt: str, user_message: str, max_tokens: int = 2048) -> str:
    """
    Async wrapper for OpenRouter Chat API (Nemotron 3).
    """
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.openrouter_http_referer,
        "X-Title": settings.openrouter_app_title,
    }
    
    payload = {
        "model": settings.openrouter_chat_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
    return data["choices"][0]["message"]["content"]
