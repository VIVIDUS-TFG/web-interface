import asyncio
from celery.signals import task_success
from celery import Celery

app = Celery('app', broker='redis://vividus_redis:6379/0', backend='redis://vividus_redis:6379/1', broker_connection_retry_on_startup=True, include=["app.tasks"])