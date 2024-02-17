import asyncio
import json
import os
from fastapi import APIRouter, BackgroundTasks, Cookie, File, Form, HTTPException, Query, Request, Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import shutil
import logging
import httpx
import aioredis
from pathlib import Path
from typing import Annotated, Dict, List

from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_302_FOUND

from celery import chain, group
from celery.result import AsyncResult

from app.celery import app as celery_app

from app.config import Settings
from app.models import Model
from app.utils import mount_models, check_service_health
from app.tasks import create_task_signatures, extract_features, notify_task_completion

from app.signals import websocket_connections

settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
router = APIRouter()

healthy_models: Dict[str, Model] = {}

@router.get("/")
async def index(request: Request):

    unchecked_models = mount_models(settings.MODELS_CONFIG)

    if not await check_service_health("http://vividus_features:8000/healthcheck"):
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Features extractor service is unhealthy.")
    
    check_tasks = [check_service_health(f"http://vividus_models_{model.name}:8000/healthcheck") for model in unchecked_models]
    results = await asyncio.gather(*check_tasks)

    unhealthy_models = []
    for model, result in zip(unchecked_models, results):
        if result:
            healthy_models[model.name] = model
        else:
            unhealthy_models.append(model.name)

    if unhealthy_models:
        detail_message = "Unhealthy models detected: " + ", ".join(unhealthy_models)
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=detail_message)
    
    model_names = list(healthy_models.keys())
    return templates.TemplateResponse("main.html", {"request": request, "model_names": model_names})

@router.post("/upload")
async def upload_file(request: Request, response: Response, file: UploadFile = File(...), options: List[str] = Form(...)):

    if any(option not in healthy_models.keys() for option in options):
        unavailable_models = [option for option in options if option not in healthy_models.keys()]
        raise HTTPException(status_code=400, detail=f"The selected model(s) '{unavailable_models}' are not available or healthy.")

    video_path = f"/videos_dir/{file.filename}"

    try:
        with open(video_path, "wb") as buffer:
            while data := await file.read(1024):  # Read chunks of 1024 bytes
                buffer.write(data)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload file {file.filename}."
        )

    data = {
        "video_path": video_path,
        "features_dir": "/features_dir"
    }

    parallel_tasks = create_task_signatures(options, data)

    workflow = chain(
        extract_features.s(data,"http://vividus_features:8000/extract_features"),
        group(parallel_tasks),
        notify_task_completion.s()
    )

    task = workflow.apply_async()

    return templates.TemplateResponse("loading.html", {"request": request, "task_id": task.id}) 

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    redis = await aioredis.from_url('redis://vividus_redis:6379/2', encoding="utf-8", decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe('task_updates')
    try:
        # Listen for messages
        async for message in pubsub.listen():
            # Check if the message is of type 'message' which indicates it's a published message
            if message['type'] == 'message':
                # Attempt to parse the JSON message data
                try:
                    data = json.loads(message['data'])
                except json.JSONDecodeError:
                    # If message is not a valid JSON, ignore and continue
                    continue

                # Check if the task_id in the message matches the task_id we're looking for
                if data.get('task_id') == task_id:
                    # If it matches, send the JSON data to the WebSocket client
                    await websocket.send_json({"status": "completed", "task_id": task_id})
                    # Optionally break or continue listening based on your use case
                    break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup: Unsubscribe and close connections
        await pubsub.unsubscribe('task_updates')
        await redis.close()
        await websocket.close()

@router.get("/results")
def results(request: Request, task_id: str = Query(...)):
    task_result = AsyncResult(task_id, app=celery_app)
    print(f"Task ID: {task_id}, State: {task_result.state}")
    if task_result.ready():
        if task_result.successful():
            result_data = task_result.get(timeout=1.0)
            return templates.TemplateResponse("main.html", {"request": request})
        else:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Task failed")
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Task not completed")