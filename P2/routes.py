from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
import requests
import tempfile
import os
import subprocess
from io import BytesIO
import numpy as np
from PIL import Image

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

@router.post("/transcode-video")
async def transcode_video_api(
    file: UploadFile = File(...),
    codec: str = "vp8"   # vp8, vp9, h265, av1
):
    """
    Front-end endpoint: receives a video and a target codec,
    sends it to ffmpeg-service /transcode, and returns the result.
    """
    codec = codec.lower()

    if codec not in ["vp8", "vp9", "h265", "av1"]:
        return JSONResponse(
            {"error": "Invalid codec. Use one of: vp8, vp9, h265, av1."},
            status_code=400
        )

    files = {"file": (file.filename, await file.read(), file.content_type)}
    params = {"codec": codec}

    r = requests.post(TRANSCODE_URL, files=files, params=params)

    if r.status_code != 200:
        # Forward error from ffmpeg-service
        return JSONResponse(
            {"error": "Transcoding failed in ffmpeg-service", "details": r.text},
            status_code=r.status_code,
        )

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
