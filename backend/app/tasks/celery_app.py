from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "focusquest",
    broker=settings.RESOLVED_CELERY_BROKER_URL,
    backend=settings.RESOLVED_CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
