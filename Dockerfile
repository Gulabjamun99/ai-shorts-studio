FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pillow pydantic sqlalchemy aiosqlite python-multipart google-genai httpx

EXPOSE 8000

CMD ["python", "run_server.py"]
