from fastapi import FastAPI, HTTPException
import subprocess
import shlex

app = FastAPI()

@app.post("/extract_features")
async def extract_features(video_path: str, features_path: str):
    try:
        safe_video_path = shlex.quote(video_path)
        safe_features_path = shlex.quote(features_path)

        result = subprocess.run(
            ["python", "main.py", "feature_type=i3d", "flow_type=pwc", f"video_paths='[{safe_video_path}]'", "on_extraction=save_numpy", f"output_path='{safe_features_path}'", "stack_size=24", "step_size=24"],
            check=True,
            capture_output=True,
            text=True
        )

        return {"message": "Extraction completed successfully.", "output": result.stdout}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Subprocess failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)