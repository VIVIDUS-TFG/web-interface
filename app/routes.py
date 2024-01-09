from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates

from app.config import Settings

settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

router = APIRouter()


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), ModelOption = Form(...)):
    # Save the uploaded file to a directory
    """ with open(f"uploads/{file.filename}", "wb") as buffer:
        while data := await file.read(1024):  # Read chunks of 1024 bytes
            buffer.write(data) """
    print(file.filename)
    print(ModelOption)