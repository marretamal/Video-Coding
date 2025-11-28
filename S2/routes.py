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

@router.post("/process-bbb")
async def process_bbb(file: UploadFile = File(...)):
    # pass the video file to the ffmpeg service for processing
    files = {"file": (file.filename, await file.read(), file.content_type)}
    
    # send POST request to ffmpeg-service for video processing
    r = requests.post(f"{FFMPEG_URL}/process-bbb", files=files)

    # return the processed video
    return StreamingResponse(
        BytesIO(r.content),
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=processed_bbb.mp4"}
    )



@router.post("/process-video-info")
async def process_video_info(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    # ffprobe to extract video info
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,bit_rate,duration",
        "-of", "default=noprint_wrappers=1", src.name
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = result.stdout.decode("utf-8").splitlines()
    video_info = {}
    for line in output:
        key, value = line.split("=")
        video_info[key] = value

    return JSONResponse(content=video_info)


@router.post("/process-chroma")
async def process_chroma(file: UploadFile = File(...), format: str = "420"):

    if format not in ["420", "422", "444"]:
        return {"error": "Invalid subsampling format. Use 420, 422, or 444."}

    files = {"file": (file.filename, await file.read(), file.content_type)}
    params = {"format": format}

    # FFmpeg service for chroma subsampling
    r = requests.post(f"{FFMPEG_URL}/chroma-subsample", files=files, params=params)

    return StreamingResponse(
        BytesIO(r.content),  
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename=subsampled_video_{format}.mp4"}
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

@router.get("/rgb-to-yuv")
def rgb_to_yuv(r: int, g: int, b: int):
    y, u, v = ColorCoordsConverter.rgb_to_yuv(r, g, b)
    return {"y": y, "u": u, "v": v}

@router.get("/yuv-to-rgb")
def yuv_to_rgb(y: float, u: float, v: float):
    r, g, b = ColorCoordsConverter.yuv_to_rgb(y, u, v)
    return {"r": r, "g": g, "b": b}

@router.post("/resize-image")
async def resize_image(file: UploadFile = File(...), width: int = 320, height: int = 240):

    files = {"file": (file.filename, await file.read(), file.content_type)}

    response = requests.post(
        f"{FFMPEG_URL}/resize",
        params={"width": width, "height": height},
        files=files
    )

    return response.json()

@router.post("/serpentine")
async def serpentine_endpoint(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False)
    src.write(await file.read())
    src.close()

    serp = serpentine(src.name)
    return {"serpentine_pixels": serp[:50]}   # return only first 50 for readability


@router.post("/compress-grayscale")
async def grayscale_compress(file: UploadFile = File(...)):

    files = {"file": (file.filename, await file.read(), file.content_type)}

    response = requests.post(
        f"{FFMPEG_URL}/grayscale",
        files=files
    )

    return response.json()


@router.post("/rle")
def rle_zero_runs(data: list[int]):
    encoded = run_length_encoding_zeros(data)
    return {"encoded": encoded}


@router.post("/dct")
async def dct_endpoint(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False)
    src.write(await file.read())
    src.close()

    blocks = DCTTools.image_to_blocks(src.name)
    d = DCTTools.dct_2d(blocks[0])
    return {"dct_first_block": np.round(d).tolist()}

@router.post("/dwt")
async def dwt_endpoint(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False)
    src.write(await file.read())
    src.close()

    blocks = DCTTools.image_to_blocks(src.name)
    coeffs = DWTTools.dwt_2d(blocks[0])
    return {"coeffs": "DWT computed successfully"}

