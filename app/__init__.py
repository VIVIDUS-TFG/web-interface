from fastapi import WebSocket
from app.celery import app as celery_app

__all__ = ('celery_app',)