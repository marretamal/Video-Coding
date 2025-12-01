from fastapi import FastAPI, UploadFile, File
import tempfile
import subprocess
import os
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse


app = FastAPI()

@app.post("/transcode")
async def transcode_video(
    file: UploadFile = File(...),
    codec: str = "vp8"  # vp8, vp9, h265, av1
):
    codec = codec.lower()

    if codec not in ["vp8", "vp9", "h265", "av1"]:
        return JSONResponse(
            {"error": "Invalid codec. Use one of: vp8, vp9, h265, av1."},
            status_code=400
        )

    # decide container and media type depending on codec
    ext_map = {
        "vp8": (".webm", "video/webm"),
        "vp9": (".webm", "video/webm"),
        "h265": (".mp4", "video/mp4"),
        "av1": (".mkv", "video/x-matroska"),
    }
    out_ext, mime_type = ext_map[codec]

    # save uploaded video to a temp file
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    out_path = src.name + f"_{codec}{out_ext}"

    # build ffmpeg command per codec
    if codec == "vp8":
        cmd = [
            "ffmpeg", "-y",
            "-i", src.name,
            "-c:v", "libvpx",
            "-b:v", "1M",
            "-c:a", "libvorbis",
            out_path,
        ]
    elif codec == "vp9":
        cmd = [
            "ffmpeg", "-y",
            "-i", src.name,
            "-c:v", "libvpx-vp9",
            "-b:v", "1M",
            "-c:a", "libopus",
            out_path,
        ]
    elif codec == "h265":
        cmd = [
            "ffmpeg", "-y",
            "-i", src.name,
            "-c:v", "libx265",
            "-preset", "medium",
            "-crf", "28",
            "-c:a", "aac",
            out_path,
        ]
    else:  # av1
        cmd = [
            "ffmpeg", "-y",
            "-i", src.name,
            "-c:v", "libaom-av1",
            "-crf", "30",
            "-b:v", "0",
            "-c:a", "libopus",
            out_path,
        ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        return JSONResponse(
            {
                "error": "ffmpeg transcoding failed",
                "details": result.stderr.decode("utf-8"),
            },
            status_code=500,
        )

    return FileResponse(
        out_path,
        media_type=mime_type,
        filename=f"output_{codec}{out_ext}"
    )


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
        "-crf", "23", # quality/compression default value
        out_path
    ]

    result=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # resized video as a downloadable file
    # return StreamingResponse(
    #     open(out_path, "rb"),
    #     media_type="video/mp4",
    #     headers={"Content-Disposition": f"attachment; filename=resized_video.mp4"}
    # )
    if result.returncode != 0:
        return {"error": f"FFmpeg failed: {result.stderr.decode()}"}

    # If successful, return the file path
    return {"output_file": out_path}

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
