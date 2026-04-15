from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # GitHub
    github_pat: str = ""

    # Storage
    storage_mode: str = "ram"          # "ram" | "disk"
    chroma_path: str = "./chroma_db"   # path for ChromaDB PersistentClient

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_http_referer: str = "http://localhost:8000"
    openrouter_app_title: str = "Drop2Life_OpenSource"
    openrouter_chat_model: str = "anthropic/claude-3.7-sonnet"

    # Embeddings provider
    embedding_provider: str = "local"   # "local" | "huggingface" | "bedrock"
    hf_api_key: str = ""
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # AWS (for Bedrock — Titan Embeddings v2)
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
