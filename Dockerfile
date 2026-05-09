FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install flask openai-whisper

COPY whisper_service.py .

RUN mkdir -p audios_whisper

EXPOSE 5001

CMD ["python", "whisper_service.py"]