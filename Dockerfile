FROM python:3.10-slim

# Installer ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p audios audios_whisper

# Initialiser records.json si absent
RUN echo "[]" > records.json

EXPOSE 5000

CMD ["python", "app.py"]