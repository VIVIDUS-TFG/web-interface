from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
import requests

from app.config import Settings

settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

router = APIRouter()


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), ModelOption = Form(...)):

    data = {
        "video_path": "/videos_dir",
        "features_path": "/features_dir"
    }

    # Save the uploaded file to a directory
    with open(f"{data.video_path}/{file.filename}", "wb") as buffer:
        while data := await file.read(1024):  # Read chunks of 1024 bytes
            buffer.write(data)

    print(file.filename)
    print(ModelOption)

    try:
        response = requests.post("http://localhost:8001/extract_features", json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
