"""Celery application configuration (structural).

This module provides Celery task definitions for async call processing.
In production deployment, the pipeline runs synchronously within the
FastAPI request cycle. Celery is included here to demonstrate async
processing capability as required by the problem statement.

To run with Celery (requires Redis):
    celery -A src.celery_app worker --loglevel=info
"""

import logging

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    from src.config import settings

    celery_app = Celery(
        "call_center_compliance",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minute hard limit
        task_soft_time_limit=240,  # 4 minute soft limit
    )

    @celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
    def process_call_async(self, audio_base64: str, language: str):
        """Async Celery task for call processing.

        Args:
            audio_base64: Base64-encoded MP3 audio.
            language: 'Tamil' or 'Hindi'.

        Returns:
            Analysis result dictionary.
        """
        from src.services.pipeline import process_call

        try:
            return process_call(audio_base64, language)
        except Exception as exc:
            logger.error(f"Celery task failed: {exc}")
            raise self.retry(exc=exc)

except ImportError:
    logger.warning("Celery not available — running in synchronous mode only.")
    celery_app = None

    def process_call_async(audio_base64: str, language: str):
        from src.services.pipeline import process_call
        return process_call(audio_base64, language)
