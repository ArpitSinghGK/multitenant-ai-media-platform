"""Celery application — the orchestration layer between the API and GPU workers."""
from __future__ import annotations

from celery import Celery

from ..config import get_settings

settings = get_settings()

celery_app = Celery(
    "aiplatform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["aiplatform.workers.tasks"],
)

celery_app.conf.update(
    task_acks_late=True,          # re-queue if a worker dies mid-job
    task_track_started=True,
    worker_prefetch_multiplier=1,  # long GPU jobs → fair dispatch, no hoarding
    task_default_queue="generation",
)
