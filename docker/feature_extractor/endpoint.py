from fastapi import FastAPI, HTTPException
import subprocess
import shlex
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class FeatureExtractionRequest(BaseModel):
    video_path: str
    features_dir: str

@app.post("/extract_features")
def extract_features(request: FeatureExtractionRequest):
    try:
        safe_video_path = shlex.quote(request.video_path)
        safe_features_dir= shlex.quote(request.features_dir)

        try:
            rgb = subprocess.run(
                ["python", "main.py", "feature_type=i3d", "flow_type=raft", f"video_paths=[{safe_video_path}]", "on_extraction=save_numpy", f"output_path={safe_features_dir}", "stack_size=24", "step_size=24", "streams=rgb"],
                check=True,
                capture_output=True,
                text=True
            )
            print("RGB Output:", rgb.stdout)
            # print("RGB Errors:", rgb.stderr)
        except subprocess.CalledProcessError as e:
            print("Error executing RGB extraction:", e)

        try:
            audio = subprocess.run(
                ["python", "main.py", "feature_type=vggish", "device=cpu", f"video_paths=[{safe_video_path}]", "on_extraction=save_numpy", f"output_path={safe_features_dir}"],
                check=True,
                capture_output=True,
                text=True
            )
            print("Audio Output:", audio.stdout)
            print("Audio Errors:", audio.stderr)
        except subprocess.CalledProcessError as e:
            print("Error executing Audio extraction:", e)

        return {"message": "Extraction completed successfully.", "output_rgb": rgb.stdout, "output_audio": audio.stdout}

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

# python main.py feature_type=vggish video_paths="[/videos_dir/Deadpool.2.2018__#0-04-46_0-05-01_label_B2-0-0.mp4]" on_extraction=save_numpy output_path="/features_dir"