# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, Response
from PIL import Image
import base64
import threading
import time
import io

app = Flask(__name__)

latest_frame = None
frame_lock = threading.Lock()

def to_jpeg(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf.read()

def mjpeg_generator():
    while True:
        with frame_lock:
            frame = latest_frame
        if frame is None:
            time.sleep(0.05)
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

@app.route("/frame", methods=["POST"])
def receive_frame():
    global latest_frame

    data = request.get_json()
    raw = base64.b64decode(data["image"])
    width = data["width"]
    height = data["height"]

    img = Image.frombytes("RGB", (width, height), raw)

    with frame_lock:
        latest_frame = to_jpeg(img)

    return jsonify({
        "status": "ok"
    })

@app.route("/video_feed")
def video_feed():
    return Response(
        mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/snapshot")
def snapshot():
    with frame_lock:
        frame = latest_frame
    if frame is None:
        return "No frame available", 204
    return Response(frame, mimetype="image/jpeg")

@app.route("/health")
def health():
    with frame_lock:
        has_frame = latest_frame is not None
    return jsonify({
        "status": "ok",
        "has_frame": has_frame
    })

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <title>NAO Live Camera</title>
      <style>
        body { background:#111; color:#0f0; font-family:monospace;
               display:flex; flex-direction:column; align-items:center;
               padding:20px; margin:0; }
        h1 { margin-bottom:20px; }
        img { border:2px solid #0f0; max-width:720px; }
      </style>
    </head>
    <body>
      <h1>NAO Live Camera Feed</h1>
      <img src="/video_feed" />
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Server running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)