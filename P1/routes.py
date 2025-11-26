from fastapi import APIRouter, UploadFile, File
import requests

from first_seminar import (
    ColorCoordsConverter,
    FFmpeg,
    serpentine,
    compress_to_grayscale,
    run_length_encoding_zeros,
    DCTTools,
    DWTTools
)
import numpy as np
from PIL import Image
import tempfile
import os

router = APIRouter()

FFMPEG_URL = "http://ffmpeg-service:9000"

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

