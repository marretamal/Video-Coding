FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY practice1.py .

EXPOSE 8000

CMD ["uvicorn", "practice1:app", "--host", "0.0.0.0", "--port", "8000"]
