from fastapi import FastAPI, HTTPException
import subprocess
import shlex
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

app = FastAPI()

class VideoClassificationRequest(BaseModel):
    video_path: str
    features_dir: str

@app.post("/classify")
def classify_video(request: VideoClassificationRequest):
    try:
        safe_features_path = shlex.quote(request.features_dir)
        rgb_list_file_path = 'list/rgb_test.list'
        audio_list_file_path = "list/audio_test.list"

        rgb_npy_files = []
        audio_npy_files = []
        for root, dirs, files in os.walk(safe_features_path):
            for file in files:
                if file.endswith('rgb.npy'):
                    absolute_path = os.path.join(root, file)
                    rgb_npy_files.append(absolute_path)
                if file.endswith('vggish.npy'):
                    absolute_path = os.path.join(root, file)
                    audio_npy_files.append(absolute_path)

        with open(rgb_list_file_path, 'w') as list_file:
            for path in rgb_npy_files:
                list_file.write(path + '\n')

        with open(audio_list_file_path, 'w') as list_file:
            for path in audio_npy_files:
                list_file.write(path + '\n')

        result = subprocess.run(
            ["python", "infer.py"],
            check=True,
            capture_output=True,
            text=True
        )

        return {"message": "Classification completed successfully.", "output": result.stdout}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Subprocess failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/healthcheck")
def healthcheck():
    return JSONResponse(content={"status": "ok"}, status_code=200)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)