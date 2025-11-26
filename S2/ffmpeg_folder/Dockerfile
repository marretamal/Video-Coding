FROM python:3.11-slim

WORKDIR /app

#install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["uvicorn", "ffmpeg_service:app", "--host", "0.0.0.0", "--port", "9000"]