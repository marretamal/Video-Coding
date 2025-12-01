**Task 1: Create a new endpoint / feature which will let you to modify the resolution (use FFmpeg in the backend)**

For this task we have started by creating two new endpoints: 
- In ffmpeg_service.py (inside S2): /resize-video -> FFmpeg resizes the video and returns the output file (default resizing is 640×360)
- In routes.py (API service, inside S2): /process-video -> Accepts upload, calls FFmpeg service, returns the video to the user
Then we wrote the necessary code in docker-compose.yml and the requierements inside both API and ffmpeg folders.

We, then, builded the docker and visited the path, we tried the endpoint POST /process-video uploading the BigBuckBunny.mp4 and choosing a smaller size to lower the resolution of the video.
<img width="835" height="787" alt="image" src="https://github.com/user-attachments/assets/a8786b6f-19b3-460f-a039-205cd6711f9f" />
<img width="990" height="364" alt="image" src="https://github.com/user-attachments/assets/e9eba214-0ee7-46c1-ba2a-d1c2e0a497d9" />

We obtained the video resized as showed in the following image:
<img width="1002" height="783" alt="image" src="https://github.com/user-attachments/assets/eae31f74-7b45-4c18-82f1-264ff40ee4f4" />

**Task 2: Create a new endpoint / feature which will let you to modify the chroma subsampling**

Chroma subsampling is a video compression technique that reduces the amount of color information (chrominance), while maintaining the luminance (brightness) resolution. 

Common chroma subsampling schemes that we have applied are:
* 4:4:4: No chroma subsampling (full color).
* 4:2:2: Horizontal chroma subsampling (resolution is halved horizontally, so that every two adjacent pixels will share the same color data). 
* 4:2:0: Both horizontal and vertical chroma subsampling. This reduces the chroma resolution by half in both directions (most common format used for video compression).
In both cases, the reduction in chroma resolution is not that noticeable to the human eye, especially if the quality of the video is not that high. 

To test the functionality, we called the /process-chroma endpoint, uploaded a video, and specified the chroma subsampling format as a parameter. 
<img width="1075" height="180" alt="image" src="https://github.com/user-attachments/assets/43eb871f-8084-4d6e-9d0a-2db2f733b1d6" />
<img width="912" height="877" alt="image" src="https://github.com/user-attachments/assets/5cee27da-d9d1-484f-bea2-ee9fdd6fcd2e" />


**Task 3: Create a new endpoint / feature which lets you read the video info and print at least 5 relevant data from the video**

We modified the ffmpeg_service.py to create a new endpoint /video-info that extracts and returns the video information using FFmpeg.

Moreover, we found that the ffprobe command can give us detailed metadata about a video. We use it to return 5 characteristics of the video: Video codec, Resolution, Duration, Bitrate, Frame rate. The output is parsed into a dictionary and returned as a JSONResponse. 

When testing the endpoint with the Big Buck Bunny video we obtained the following result:
<img width="981" height="285" alt="image" src="https://github.com/user-attachments/assets/ee825826-0df0-4ba8-a32c-6ca4da75b641" />

This indicates the video information such that: 
* codec_name: The codec used for the video (in this case, h264).
* width and height: The resolution of the video (640x360).
* r_frame_rate: The frame rate of the video (30 frames per second).
* duration: The duration of the video (634.566667 seconds).
* bit_rate: The bit rate of the video (227570).


**Task 4**

To complete this task, we followed these steps (code that we implemented in ffmpeg_service.py): 
1. Save the uploaded file: We temporarily save the uploaded BBB video using NamedTemporaryFile.
2. Cut the video to 20 seconds: We use FFmpeg with -t 00:00:20 to trim the video to a 20-second segment.
3. Extract and convert audio to different formats: AAC (mono) using the -ac 1 flag for mono audio. MP3 (stereo with lower bitrate)using -ac 2 for stereo and a 96k bitrate for compression. AC3 using the ac3 codec.
4. Combine video and audio: We use FFmpeg to combine the video and the three audio streams (AAC, MP3, AC3) into one .mp4 file using the -map option to specify which streams to use.
5. Return the final video: The processed .mp4 file is returned as a FileResponse. 

When downloading the resulting processed video, we can see that it is in fact 20 seconds long and inspecting its characteristics using ffprobe we can see that it actually has 3 different audio streams (aac, mp3, ac3). 

<img width="798" height="618" alt="image" src="https://github.com/user-attachments/assets/fe547a68-d1e2-45b0-8593-258c00f75f4f" />
<img width="796" height="495" alt="image" src="https://github.com/user-attachments/assets/e9b51eba-73a1-45fb-9e00-2b9d9a910ff1" />

**Task 5**

For this task we implemented the track-count logic inside the FFmpeg service and the corresponding endpoint in the main API. For the track -count logic we run ffprobe on the uploaded file, read all the streams inside the MP4 container, count how many are video/audio/subtitle tracks, and return the totals.
Here’s the result obtained when testing the endpoint with the Big Buck Bunny video:

<img width="770" height="499" alt="Screenshot 2025-12-01 at 14 26 38" src="https://github.com/user-attachments/assets/74c65431-cffa-412f-a064-2d31f6ecb246" />


**Task 6**

To visualize macroblocks and motion vectors, FFmpeg provides the following debugging filter:
-vf codecview=mv=pf+bf+bb

This filter draws:
* pf — forward predicted motion vectors
* bf — backward motion vectors
* bb — bidirectional motion vectors
* Macroblock boundaries are visible because codecview outlines them.

For this task, the endpoint implementation consisted of the following steps:
1. Save the uploaded video temporarily, so FFmpeg can access it.
2. Use the FFmpeg flag:
* -flags2 +export_mvs
This tells FFmpeg to export motion vectors for visualization.
3. Apply the video filter:
* -vf codecview=mv=pf+bf+bb
This overlays the motion vectors on the video.
4. Return the processed video as the endpoint response so the user can download or view it.


**Task 7**

FFmpeg already has a built-in filter for generating a YUV histogram video: the histogram filter. 

We created a new FastAPI endpoint in ffmpeg_service.py that accepts a video upload: Runs FFmpeg to generate a histogram video and returns the new MP4 file. Then, the API gateway (routes.py) forwards the video like the other endpoints.

For the ffmpeg_service.py endpoint:
* -vf histogram,format=yuv420p  applies the histogram filter and converts the video to a playable YUV420p format
* -c:v libx264 encodes the video using the H.264 codec

For the routes.py endpoint, the output video shows three stacked histograms, one for each channel (Y, U, and V) as the following image:

<img width="614" height="914" alt="Screenshot 2025-12-01 at 12 06 34" src="https://github.com/user-attachments/assets/65c5e456-a211-4c72-a46d-9acde42b0b4b" />


