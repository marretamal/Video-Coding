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
