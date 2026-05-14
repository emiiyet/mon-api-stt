from flask import Flask, request, jsonify
from groq import Groq
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

UPLOAD_FOLDER = "audios_whisper"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_to_wav(input_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", output_path
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print("Erreur ffmpeg:", str(e))
        return False

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "whisper-groq"})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["audio"]
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    webm_path = os.path.join(UPLOAD_FOLDER, f"audio_{now}.webm")
    wav_path  = os.path.join(UPLOAD_FOLDER, f"audio_{now}.wav")

    file.save(webm_path)

    if not convert_to_wav(webm_path, wav_path):
        return jsonify({"error": "Conversion échouée"}), 500

    try:
        with open(wav_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        print(f"✅ Transcription: {text}")
        return jsonify({"text": text})
    except Exception as e:
        print("Erreur Groq Whisper:", str(e))
        return jsonify({"error": "Transcription échouée"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)