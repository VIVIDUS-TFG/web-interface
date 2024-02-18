from __future__ import absolute_import, unicode_literals
import asyncio
import json
import redis
from fastapi import WebSocket

import requests
from typing import List
from .celery import app

redis_client = redis.Redis(host='vividus_redis', port=6379, db=2)

def publish_task_completion(task_id):
    message = json.dumps({"task_id": task_id})
    redis_client.publish('task_updates', message)

def create_task_signatures(classification_options: List[str], payload: dict) -> List[str]:
    task_signatures = []
    for option in classification_options:
        task_signatures.append(classify_video.s(payload, f"http://vividus_models_{option}:8000/classify"))

    return task_signatures

@app.task
def extract_features(payload: dict, endpoint_url: str):
    try:
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        raise extract_features.retry(exc=e, max_retries=3, countdown=60)
    except Exception as e:
        raise e
    
@app.task
def classify_video(parent_result: bool, payload: dict, endpoint_url: str):
    try:
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        raise classify_video.retry(exc=http_err, max_retry=3, countdown=60)
    except requests.RequestException as err:
        raise classify_video.retry(exc=err, max_retries=3, countdown=60)
    except Exception as e:
        raise e
    
@app.task(bind=True)
def notify_task_completion(self, parent_result: dict):
    task_id = self.request.id
    publish_task_completion(task_id)
    return parent_result

