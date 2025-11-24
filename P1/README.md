**Task 1: Create and API and put it inside a Docker**

First, we created a simple FastAPI in the file practice.py, which returns the message: Hello, Practice1!, just to check that it works correctly. 

To complete the task, we needed Docker Desktop installed and running. Docker allows us to package our API inside a container.

From the terminal, we built the Docker image as: docker build -t practice1-api .
And ran the container: docker run -p 8000:8000 practice1-api

After running the container, we opened the website http://localhost:8000 and we could see our message 

![alt text](image.png)
