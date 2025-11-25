**Task 1: Create and API and put it inside a Docker**

First, we created a simple FastAPI in the file practice.py, which returns the message: Hello, Practice1!, just to check that it works correctly. 

To complete the task, we needed Docker Desktop installed and running. Docker allows us to package our API inside a container.

From the terminal, we built the Docker image as: docker build -t practice1-api .
And ran the container: docker run -p 8000:8000 practice1-api

After running the container, we opened the website http://localhost:8000 and we could see our message 

![alt text](image.png)

**Task 2: Put ffmpeg inside a Docker**
First, to add FFmpeg, we installed it inside the container by adding the corresponding lines to the Dockerfile in Visual Studio.
Then we rebuilt the Docker image as before and ran the container again.

We tested whether FFmpeg was correctly installed inside the running container by opening a new terminal with:
docker exec -it <container_id> bash
and checking the version with:
ffmpeg -version
We obtained the following response from the running container:
![alt text](img_t2.png)
![alt text](img_t2.1.png)

**Task 3: Include all your previous work inside the new API. Use the help of any AI tool to adapt the code and the unit tests**
To do so, we started by creating a new file inside the P1 folder called routes.py, and we duplicated the file first_seminar.py inside the same folder.

We imported the functions from first_seminar into the routes.py file and created FastAPI endpoints for each operation.

Next, we imported the router into the practice1 file (the main API file) to ensure that all endpoints were activated at once.
After that, we rebuilt and ran the Docker container. We obtained the following active endpoints in our local host browser under /docs (http://localhost:8000/docs):

![alt text](img_t3.png)
![alt text](img_t3.1.png)

For the test 