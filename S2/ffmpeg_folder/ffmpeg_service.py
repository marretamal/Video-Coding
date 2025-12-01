from fastapi import FastAPI, UploadFile, File
import tempfile
import subprocess
import os
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse


app = FastAPI()

@app.post("/yuv-histogram")
async def yuv_histogram(file: UploadFile = File(...)):
    # Save uploaded video to a temporary file
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    try:
        src.write(await file.read())
    finally:
        src.close()

    output_path = src.name.replace(".mp4", "_yuv_hist.mp4")

    # Simple FFmpeg command to generate the histogram visualization (YUV), produces a histogram image per frame
    cmd = [
        "ffmpeg",
        "-y",
        "-i", src.name,
        "-vf", "histogram,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        output_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Clean up source file
    try:
        os.remove(src.name)
    except Exception:
        pass

    if result.returncode != 0:
        # Return FFmpeg stderr for debugging
        return JSONResponse(status_code=500, content={
            "error": "FFmpeg failed to generate histogram",
            "ffmpeg_stderr": result.stderr.decode(errors="ignore")
        })

    return FileResponse(output_path, media_type="video/mp4", filename="yuv_histogram.mp4")


@app.post("/motion-vectors")
async def motion_vectors(file: UploadFile = File(...)):
    # Save uploaded video to a temporary file
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()
    video_path = src.name

    # Output video path
    out_path = video_path.replace(".mp4", "_motion_vectors.mp4")

    # FFmpeg command to visualize motion vectors
    cmd = [
        "ffmpeg",
        "-y",
        "-flags2", "+export_mvs",          # export motion vectors
        "-i", video_path,
        "-vf", "codecview=mv=pf+bf+bb",   # display motion vectors
        "-preset", "fast",
        out_path
    ]

    # Run FFmpeg
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return {"error": f"FFmpeg failed: {result.stderr.decode()}"}

    # Return the processed video
    return FileResponse(out_path, media_type="video/mp4", filename="motion_vectors.mp4")







@app.post("/count-tracks")
async def count_tracks(file: UploadFile = File(...)):
    # Save uploaded video to a temporary file
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    # ffprobe: extract all streams (audio/video/subtitle/etc.)
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=index,codec_type",
        "-of", "json",
        src.name
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    import json
    info = json.loads(result.stdout.decode("utf-8"))

    streams = info.get("streams", [])

    video_tracks = sum(1 for s in streams if s.get("codec_type") == "video")
    audio_tracks = sum(1 for s in streams if s.get("codec_type") == "audio")
    subtitle_tracks = sum(1 for s in streams if s.get("codec_type") == "subtitle")

    return {
        "total_tracks": len(streams),
        "video_tracks": video_tracks,
        "audio_tracks": audio_tracks,
        "subtitle_tracks": subtitle_tracks
    }


@app.post("/process-bbb")
async def process_bbb(file: UploadFile = File(...)):
    # Save the uploaded video temporarily
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    video_path = src.name

    # cut the video to 20 seconds
    cut_video_path = video_path.replace(".mp4", "_20s.mp4")
    cmd_cut = [
        "ffmpeg", "-y", "-i", video_path, "-t", "00:00:20", "-c", "copy", cut_video_path
    ]
    subprocess.run(cmd_cut, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # export audio as AAC (mono)
    audio_aac_path = video_path.replace(".mp4", "_audio_aac_mono.aac")
    cmd_aac = [
        "ffmpeg", "-y", "-i", cut_video_path, "-vn", "-acodec", "aac", "-ac", "1", audio_aac_path
    ]
    subprocess.run(cmd_aac, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # export audio as MP3 
    audio_mp3_path = video_path.replace(".mp4", "_audio_mp3_stereo.mp3")
    cmd_mp3 = [
        "ffmpeg", "-y", "-i", cut_video_path, "-vn", "-acodec", "libmp3lame", "-ac", "2", "-ab", "96k", audio_mp3_path
    ]
    subprocess.run(cmd_mp3, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # export audio as AC3
    audio_ac3_path = video_path.replace(".mp4", "_audio_ac3.ac3")
    cmd_ac3 = [
        "ffmpeg", "-y", "-i", cut_video_path, "-vn", "-acodec", "ac3", audio_ac3_path
    ]
    subprocess.run(cmd_ac3, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # combine the video and all audio into a single .mp4
    output_video_path = video_path.replace(".mp4", "_final.mp4")
    cmd_combine = [
        "ffmpeg", "-y", "-i", cut_video_path, "-i", audio_aac_path, "-i", audio_mp3_path, "-i", audio_ac3_path,
        "-map", "0:v:0", "-map", "1:a:0", "-map", "2:a:0", "-map", "3:a:0", "-c:v", "libx264", "-c:a", "aac",
        "-c:a:1", "libmp3lame", "-c:a:2", "ac3", "-shortest", output_video_path
    ]
    subprocess.run(cmd_combine, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Return the processed video file
    return FileResponse(output_video_path, media_type="video/mp4", filename="processed_bbb.mp4")

@app.post("/video-info")
async def video_info(file: UploadFile = File(...)):
    src = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    src.write(await file.read())
    src.close()

    # run ffprobe to get video info
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", 
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,bit_rate,duration", 
        "-of", "default=noprint_wrappers=1", src.name
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pass the output into a dictionary
    output = result.stdout.decode("utf-8").splitlines()
    video_info = {}
    
    for line in output:
        key, value = line.split("=")
        video_info[key] = value

    # Return the relevant video information
    return JSONResponse(content=video_info)


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
