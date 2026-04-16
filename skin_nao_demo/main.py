import subprocess
import os
from pathlib import Path
import shutil
import uuid
from datetime import datetime

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from predictor import predict_image, build_speech_text

app = FastAPI(title="Skin NAO Demo API")

NAO_CAMERA_SERVER_URL = "http://YOUR_NAO_CAMERA_SERVER_IP:5000/snapshot"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

CAPTURED_DIR = BASE_DIR / "captured_images"
CAPTURED_DIR.mkdir(exist_ok=True)

app.mount("/captured_images", StaticFiles(directory=str(CAPTURED_DIR)), name="captured_images")

PYTHON2_PATH = r"C:\Path\To\Python27\python.exe"
NAO_SPEAKER_SCRIPT = BASE_DIR / "nao_speaker.py"


@app.get("/")
def root():
    return {"message": "Skin NAO Demo API is running."}


@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    suffix = Path(file.filename).suffix if file.filename else ".png"
    temp_filename = f"{uuid.uuid4().hex}{suffix}"
    temp_path = UPLOAD_DIR / temp_filename

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = predict_image(str(temp_path))
        speech_text = build_speech_text(result)

        try:
            predicted_code = result.get("predicted_class_code") or result.get("predicted_class")
            speak_with_nao(speech_text, predicted_code)
        except Exception as e:
            print("NAO speech error:", e)

        response_data = {
            "success": True,
            "filename": file.filename,
            "source": "uploaded_file",
            "predicted_index": result.get("predicted_index"),
            "predicted_class_code": result.get("predicted_class_code", result.get("predicted_class")),
            "predicted_class_name": result.get("predicted_class_name", result.get("predicted_class")),
            "confidence": result.get("confidence"),
            "top_predictions": result.get("top_predictions", []),
            "all_predictions": result.get("all_predictions", []),
            "speech_text": speech_text
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.post("/predict_from_nao")
def predict_from_nao():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"captured_{timestamp}.jpg"
    saved_path = CAPTURED_DIR / saved_filename

    try:
        response = requests.get(NAO_CAMERA_SERVER_URL, timeout=10)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not capture image from NAO camera.")

        with saved_path.open("wb") as f:
            f.write(response.content)

        result = predict_image(str(saved_path))
        speech_text = build_speech_text(result)

        try:
            predicted_code = result.get("predicted_class_code") or result.get("predicted_class")
            speak_with_nao(speech_text, predicted_code)
        except Exception as e:
            print("NAO speech error:", e)

        response_data = {
            "success": True,
            "filename": saved_filename,
            "source": "nao_camera",
            "captured_image_url": f"http://YOUR_BACKEND_IP:8000/captured_images/{saved_filename}",
            "predicted_index": result.get("predicted_index"),
            "predicted_class_code": result.get("predicted_class_code", result.get("predicted_class")),
            "predicted_class_name": result.get("predicted_class_name", result.get("predicted_class")),
            "confidence": result.get("confidence"),
            "top_predictions": result.get("top_predictions", []),
            "all_predictions": result.get("all_predictions", []),
            "speech_text": speech_text
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NAO camera prediction failed: {str(e)}")


def speak_with_nao(text: str, predicted_class_code: str | None):
    if not text.strip():
        return

    if not PYTHON2_PATH or not Path(PYTHON2_PATH).exists():
        print("Python 2 interpreter not found. Skipping NAO speech.")
        return

    if not NAO_SPEAKER_SCRIPT.exists():
        print("nao_speaker.py not found. Skipping NAO speech.")
        return

    predicted_class_code = predicted_class_code or ""

    print("Sending to NAO:", text)
    print("With class code:", predicted_class_code)

    result = subprocess.run(
        [PYTHON2_PATH, str(NAO_SPEAKER_SCRIPT), text, predicted_class_code],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )

    print("NAO stdout:", result.stdout)
    print("NAO stderr:", result.stderr)
    print("NAO return code:", result.returncode)
