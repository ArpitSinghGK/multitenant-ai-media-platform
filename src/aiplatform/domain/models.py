"""Provider-agnostic domain types shared across the Control Plane and AI Plane.

Nothing here references a concrete AI provider — that isolation is the whole point:
business logic depends on `Modality` + capability, never on "AudioCraft" or "RVC".
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Modality(str, Enum):
    LYRICS = "lyrics"
    MUSIC = "music"
    VOICE = "voice"
    VIDEO = "video"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Role(str, Enum):
    """RBAC roles resolved from the Supabase JWT."""
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    MEMBER = "member"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TenantContext(BaseModel):
    """The resolved caller: which organization, which user, what they may do.

    Populated by the auth dependency from a verified JWT and threaded through
    every service call so multi-tenancy is enforced by construction.
    """
    org_id: str
    user_id: str
    role: Role = Role.MEMBER
    plan_code: str = "free"


class GenerationRequest(BaseModel):
    modality: Modality
    prompt: str = Field(min_length=1, max_length=8_000)
    # Optional hard pin; when omitted the registry picks by capability + policy.
    provider: str | None = None
    params: dict = Field(default_factory=dict)


class Job(BaseModel):
    id: str = Field(default_factory=_uuid)
    org_id: str
    user_id: str
    modality: Modality
    provider: str
    status: JobStatus = JobStatus.QUEUED
    credits_hold: int = 0
    request: dict = Field(default_factory=dict)
    result_url: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ProviderResult(BaseModel):
    """Normalized output every adapter returns, regardless of upstream shape."""
    provider: str
    artifact_url: str
    duration_ms: int = 0
    meta: dict = Field(default_factory=dict)
