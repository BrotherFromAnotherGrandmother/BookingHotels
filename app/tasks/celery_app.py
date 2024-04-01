from celery import Celery
from app.config import settings
from celery.schedules import crontab

celery_worker = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled",

    ],
)

celery_worker.conf.beat_schedule = {
    "luboe-nazvanie_key": {
        "task": "periodic_task",
        "schedule": 10,
        # "schedule": crontab(minute="30", hour="15") более простое выставление времени
    }
}
