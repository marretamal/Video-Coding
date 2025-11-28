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







