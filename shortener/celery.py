"""
@file celery-app.py
@author Antony Chiossi
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shortener.settings")

app = Celery("shortener")
app.conf.task_track_started = True
app.conf.task_time_limit = 30
app.conf.task_soft_time_limit = 20
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    "delete-expired-urls": {
        "task": "shortener.tasks.delete_expired_urls",
        "schedule": crontab(minute="*"),
    }
}
app.autodiscover_tasks()
