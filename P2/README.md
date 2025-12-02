**Task 1**

In this task, we created a new API endpoint that converts any input video into one of the following modern codecs: VP8, VP9, H.265 / HEVC and AV1.
The transcoding is performed by the FFmpeg service running inside Docker, using the proper encoder for each format:
- libvpx (VP8) → .webm
- libvpx-vp9 (VP9) → .webm
- libx265 (H.265) → .mp4
- libaom-av1 (AV1) → .mkv

We have checked that it works correctly:
<img width="1096" height="799" alt="image" src="https://github.com/user-attachments/assets/ac3372a5-f9f5-43e8-a00e-ff469b13168b" />

Using ffprobe we checked the characteristics of the downloaded videos and we can see that in fact the conversions are done correctly:
<img width="1085" height="416" alt="image" src="https://github.com/user-attachments/assets/1f672280-f641-4fc1-856c-10ef33c4df53" />

**Task 2** 

In this task we implemented an encoding ladder which generates several versions of the same input video, each at a different resolution.

We have chosen to return the following output resolutions: 426x240, 640x360, 854x480, 1280x720, 1920x1080. For each resolution, the endpoint calls the previously created resize method (request to the ffmpeg-service), which performs video scaling and saves each output into a zip.

<img width="931" height="1000" alt="image" src="https://github.com/user-attachments/assets/54445774-79de-4f50-98d8-6404b7891f5e" />

When executing the endpoint we can see the several requests to the ffmpeg-service, one for each resolution:
<img width="1121" height="578" alt="image" src="https://github.com/user-attachments/assets/cbd51fcc-21da-4d9b-8031-0c71fdc24da0" />

The downloaded file is a zip called encoding_ladder.zip which contains the video with the different resolutions defined. 
<img width="816" height="355" alt="image" src="https://github.com/user-attachments/assets/43cbc267-5dbb-49ad-bcfd-e85557b23cda" />

**Task 3**

For the final part of the project, we implemented a simple web GUI that interacts with our FastAPI backend.
The frontend webpage (templates/index.html) allows users to:
- Upload a video file
- Transcode it to another codec (selecting between VP8, VP9, H.265, or AV1)
- Trigger encoding ladder generation
- Analyze the video
We also created a CSS file inside /static/ to improve the visual appearance.
The GUI is integrated into FastAPI using Jinja2Templates for HTML rendering and StaticFiles for serving CSS.

Explanation of the FastAPI setup:
1. FastAPI app instance: app = FastAPI() creates the main application.
2. Static files: app.mount("/static", ...) serves files like CSS or JS so the frontend can use them.
3. Templates: Jinja2Templates(directory="templates") allows rendering HTML pages dynamically.
4. API routes: app.include_router(router) imports additional routes from routes.py.
5. Home route: The / endpoint renders index.html and passes the request object needed by Jinja2.

The GUI performs requests to our existing API endpoints: /transcode-video, /encoding-ladder, /resize-video and the API processes the videos with FFmpeg. 

The processed result is returned directly to the GUI so the user can download it. The GUI becomes available at: http://localhost:8000
Here’s our first version of the GUI:
<img width="1072" height="1023" alt="image" src="https://github.com/user-attachments/assets/df303e17-15b0-415c-8db7-84cd3eec6b60" />

**Task 4:**

For this last task, using AI we did the following two implementations:

1. GUI Improvements: The original user interface was upgraded to a more fun, modern, and visually appealing GUI.

- A complete redesign of the HTML page, removing plain layout and adding a aesthetic structure.
- Added a modern gradient background for a dynamic and creative visual experience.
- Introduced Google Fonts (Poppins) for a fresh and fun typography style.
- Added highlight (yellow) colors, shadows, soft edges, and improved spacing.
- Added interactive buttons for better user engagement.

All styling is done directly inside index.html.

Here’s our renovated interface:
<img width="1112" height="1058" alt="image" src="https://github.com/user-attachments/assets/8ff3a384-c1b4-4199-ac29-aa76ae80f55e" />


2. Unit Tests: To ensure that the API works correctly, we added a set of automated unit tests using pytest and FastAPI's TestClient.

We created a file named test_api.py containing:
- Tests for transcoding into VP8, VP9, H265
- Test verifying the /encoding-ladder endpoint returns a ZIP file

The tests require a small input video to run. Therefore, we added: test_files/sample.mp4.This file has been omitted in github since it was required not to upload any videos. 

The output lists all passing and failing tests, ensuring that the backend behaves correctly.
<img width="1187" height="714" alt="image" src="https://github.com/user-attachments/assets/49bbba11-e583-4630-8e60-723fac1aeb88" />

We created a separate file 'changes.txt' to define the new changes that AI has implemented with respect to the new GUI interface and the file optimization. 



