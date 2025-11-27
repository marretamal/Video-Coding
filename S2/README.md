**Task 1: Create a new endpoint / feature which will let you to modify the resolution (use FFmpeg in the backend)**
For this task we have started by creating two new endpoints: 
- In ffmpeg_service.py (inside S2): /resize-video -> FFmpeg resizes the video and returns the output file (default resizing is 640×360)
- In routes.py (API service, inside S2): /process-video -> Accepts upload, calls FFmpeg service, returns the video to the user
Then we wrote the necessary code in docker-compose.yml and the requierements inside both API and ffmpeg folders.

We, then, builded the docker and visited the path, we tried the endpoint POST /process-video uploading the BigBuckBunny.mp4.
We obtained the video resized as showed in the followoing timage:

**Task 2: Create a new endpoint / feature which will let you to modify the chroma subsampling**