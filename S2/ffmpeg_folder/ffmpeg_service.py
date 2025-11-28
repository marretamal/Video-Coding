from fastapi import FastAPI, UploadFile, File
import tempfile
import subprocess
import os
from fastapi.responses import StreamingResponse, FileResponse

app = FastAPI()

@app.post("/chroma-subsample")
async def chroma_subsample(
    file: UploadFile = File(...),
    format: str = "420"  # default to 420 (yuv420p)
):
    # format options to pixel formats
    pix_format_map = {
        "444": "yuv444p",
        "422": "yuv422p",
        "420": "yuv420p"
    }

    if format not in pix_format_map:
        return {"error": "Invalid subsampling format. Use 444, 422, or 420."}

    # save uploaded file
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    out_path = src.name + f"_subsampled_{format}.mp4"

    # FFmpeg command to apply chroma subsampling
    cmd = [
        "ffmpeg", "-y",
        "-i", src.name,
        "-pix_fmt", pix_format_map[format],  # chroma subsampling command
        "-preset", "fast",
        "-crf", "23",  # quality/compression
        out_path
    ]

    # process the video
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # processed video file
    return FileResponse(out_path, media_type="video/mp4", filename=f"video_subsampled_{format}.mp4")

@app.post("/resize-video")
async def resize_video(
    file: UploadFile = File(...),
    width: int = 640,
    height: int = 360
):
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    out_path = src.name + "_resized.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", src.name,
        "-vf", f"scale={width}:{height}",
        "-preset", "fast",
        "-crf", "23",
        out_path
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # resized video as a downloadable file
    return StreamingResponse(
        open(out_path, "rb"),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename=resized_video.mp4"}
    )

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
