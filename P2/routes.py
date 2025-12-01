from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
import requests
import tempfile
import os
import subprocess
from io import BytesIO
import numpy as np
from PIL import Image
import zipfile

from first_seminar import (
    ColorCoordsConverter,
    FFmpeg,
    serpentine,
    compress_to_grayscale,
    run_length_encoding_zeros,
    DCTTools,
    DWTTools
)

router = APIRouter()

FFMPEG_URL = "http://ffmpeg-service:9000" 
TRANSCODE_URL = f"{FFMPEG_URL}/transcode"

@router.post("/encoding-ladder")
async def encoding_ladder(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    input_path = src.name

    #encoding ladder resolutions we have chosen
    ladder = [
        {"width": 426, "height": 240},
        {"width": 640, "height": 360},
        {"width": 854, "height": 480},
        {"width": 1280, "height": 720},
        {"width": 1920, "height": 1080},
    ]

    # prepare an in-memory ZIP file
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for step in ladder:
            w = step["width"]
            h = step["height"]

            # request to ffmpeg-service
            r = requests.post(
                "http://ffmpeg-service:9000/resize-video",
                files={"file": (file.filename, open(input_path, "rb"), "video/mp4")},
                params={"width": w, "height": h}
            )

            # save each output into the ZIP
            filename = f"video_{w}x{h}.mp4"
            zipf.writestr(filename, r.content)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=encoding_ladder.zip"
        }
    )


@router.post("/transcode-video")
async def transcode_video_api(
    file: UploadFile = File(...),
    codec: str = "vp8"   # vp8, vp9, h265, av1
):
   
    codec = codec.lower()

    if codec not in ["vp8", "vp9", "h265", "av1"]:
        return JSONResponse(
            {"error": "Invalid codec. Use one of: vp8, vp9, h265, av1."},
            status_code=400
        )

    files = {"file": (file.filename, await file.read(), file.content_type)}
    params = {"codec": codec}

    r = requests.post(TRANSCODE_URL, files=files, params=params)

    ext_map = {
        "vp8": (".webm", "video/webm"),
        "vp9": (".webm", "video/webm"),
        "h265": (".mp4", "video/mp4"),
        "av1": (".mkv", "video/x-matroska"),
    }
    out_ext, mime_type = ext_map[codec]

    return StreamingResponse(
        BytesIO(r.content),
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename=transcoded_{codec}{out_ext}"}
    )


@router.post("/resize-video")
async def resize_video(file: UploadFile = File(...), width: int = 640, height: int = 360):
    files = {"file": (file.filename, await file.read(), file.content_type)}
    params = {"width": width, "height": height}

    # FFmpeg service for resizing
    r = requests.post(f"{FFMPEG_URL}/resize-video", files=files, params=params)

    return StreamingResponse(
        BytesIO(r.content),
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=resized_video.mp4"}
    )


@router.post("/process-video")
async def process_video(
    file: UploadFile = File(...),
    width: int = 640,
    height: int = 360
):
    files = {"file": (file.filename, await file.read(), file.content_type)}
    params = {"width": width, "height": height}

    r = requests.post(FFMPEG_URL, files=files, params=params)

    return StreamingResponse(
        content=iter([r.content]),
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=resized_video.mp4"}
    )
