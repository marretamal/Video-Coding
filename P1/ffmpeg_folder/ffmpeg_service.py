from fastapi import FastAPI, UploadFile, File
import tempfile
import subprocess
import os

app = FastAPI()

@app.post("/resize")
async def resize(file: UploadFile = File(...), width: int = 320, height: int = 240):
    # Save the input file
    src = tempfile.NamedTemporaryFile(delete=False)
    src.write(await file.read())
    src.close()

    out_path = src.name + "_resized.png"

    # Call FFmpeg CLI
    cmd = [
        "ffmpeg", "-y",
        "-i", src.name,
        "-vf", f"scale={width}:{height}",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {"output_file": out_path}

@app.post("/grayscale")
async def grayscale(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False)
    src.write(await file.read())
    src.close()

    out_path = src.name + "_gray.jpg"

    cmd = [
        "ffmpeg", "-y",
        "-i", src.name,
        "-vf", "format=gray",
        "-qscale:v", "31",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {"output_file": out_path}
