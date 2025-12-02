from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import tempfile
import subprocess
import json

app = FastAPI()


# ------------------------------
# Small helpers to reduce code
# ------------------------------
def save_temp(file: UploadFile, suffix=".mp4"):
    """Save an uploaded file to a temporary location."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file)
    tmp.close()
    return tmp.name

def run_cmd(cmd):
    """Run a subprocess command and return (success, stdout, stderr)."""
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0, result.stdout.decode(), result.stderr.decode()


# ------------------------------
#  Endpoint: /transcode
# ------------------------------
@app.post("/transcode")
async def transcode_video(file: UploadFile = File(...), codec: str = "vp8"):

    codec = codec.lower()
    if codec not in ["vp8", "vp9", "h265", "av1"]:
        return JSONResponse({"error": "Invalid codec"}, status_code=400)

    ext_map = {
        "vp8": (".webm", "video/webm", ["libvpx", "1M", "libvorbis"]),
        "vp9": (".webm", "video/webm", ["libvpx-vp9", "1M", "libopus"]),
        "h265": (".mp4", "video/mp4", ["libx265", "medium", "28", "aac"]),
        "av1": (".mkv", "video/x-matroska", ["libaom-av1", "30", "0", "libopus"]),
    }

    out_ext, mime_type, params = ext_map[codec]

    src_path = save_temp(await file.read())
    out_path = src_path + f"_{codec}{out_ext}"

    if codec in ["vp8", "vp9"]:
        vcodec, bitrate, acodec = params
        cmd = ["ffmpeg", "-y", "-i", src_path, "-c:v", vcodec, "-b:v", bitrate, "-c:a", acodec, out_path]
    elif codec == "h265":
        vcodec, preset, crf, acodec = params
        cmd = ["ffmpeg", "-y", "-i", src_path, "-c:v", vcodec, "-preset", preset, "-crf", crf, "-c:a", acodec, out_path]
    else:  # av1
        vcodec, crf, bitrate, acodec = params
        cmd = ["ffmpeg", "-y", "-i", src_path, "-c:v", vcodec, "-crf", crf, "-b:v", bitrate, "-c:a", acodec, out_path]

    ok, _, err = run_cmd(cmd)

    if not ok:
        return JSONResponse({"error": "ffmpeg failed", "details": err}, status_code=500)

    return FileResponse(out_path, media_type=mime_type, filename=f"output_{codec}{out_ext}")


# ------------------------------
#  Endpoint: /resize-video
# ------------------------------
@app.post("/resize-video")
async def resize_video(file: UploadFile = File(...), width: int = 640, height: int = 360):

    src_path = save_temp(await file.read())
    out_path = src_path + "_resized.mp4"

    cmd = ["ffmpeg", "-y", "-i", src_path, "-vf", f"scale={width}:{height}", "-preset", "fast", "-crf", "23", out_path]
    ok, _, err = run_cmd(cmd)

    if not ok:
        return JSONResponse({"error": "FFmpeg failed", "details": err}, status_code=500)

    return {"output_file": out_path}


# ------------------------------
#  Endpoint: /resize (image)
# ------------------------------
@app.post("/resize")
async def resize(file: UploadFile = File(...), width: int = 320, height: int = 240):

    src_path = save_temp(await file.read(), suffix="")
    out_path = src_path + "_resized.png"

    cmd = ["ffmpeg", "-y", "-i", src_path, "-vf", f"scale={width}:{height}", out_path]
    run_cmd(cmd)

    return {"output_file": out_path}


# ------------------------------
#  Endpoint: /grayscale
# ------------------------------
@app.post("/grayscale")
async def grayscale(file: UploadFile = File(...)):

    src_path = save_temp(await file.read(), suffix="")
    out_path = src_path + "_gray.jpg"

    cmd = ["ffmpeg", "-y", "-i", src_path, "-vf", "format=gray", "-qscale:v", "31", out_path]
    run_cmd(cmd)

    return {"output_file": out_path}


# ------------------------------
#  Endpoint: /video-info
# ------------------------------
@app.post("/video-info")
async def video_info(file: UploadFile = File(...)):

    src_path = save_temp(await file.read())

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        src_path
    ]

    ok, out, err = run_cmd(cmd)
    if not ok:
        return JSONResponse({"error": "ffprobe failed", "details": err}, status_code=500)

    info = json.loads(out)

    # Extract only the video stream
    video_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video_stream:
        return JSONResponse({"error": "No video stream found"}, status_code=400)

    return {
        "codec_name": video_stream.get("codec_name"),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "r_frame_rate": video_stream.get("r_frame_rate"),
        "duration": info.get("format", {}).get("duration"),
        "bit_rate": video_stream.get("bit_rate") or info.get("format", {}).get("bit_rate"),
    }
