"""Typed application settings, sourced from environment / .env (see .env.example)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_name: str = "Multi-Tenant AI Media Platform"
    log_level: str = "INFO"

    # Control-plane state
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/aiplatform"

    # Queue / cache
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Auth (self-hosted Supabase)
    supabase_url: str = "http://localhost:8000"
    supabase_jwt_secret: str = "change-me"

    # GPU workers (RunPod Serverless) — keyed per provider adapter.
    runpod_api_key: str = ""
    runpod_endpoint_audiocraft: str = ""
    runpod_endpoint_amphion: str = ""
    runpod_endpoint_openvoice: str = ""
    runpod_endpoint_rvc: str = ""
    runpod_endpoint_comfyui: str = ""

    artifact_bucket_url: str = "s3://ai-artifacts"
    artifact_signed_url_ttl: int = 3600


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so settings are parsed once per process."""
    return Settings()
