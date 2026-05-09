from flask import Flask, request, jsonify
import whisper
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

# Charger le modèle Whisper
print("🔄 Chargement du modèle Whisper...")
model = whisper.load_model("tiny")
print("✅ Modèle Whisper prêt !")

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
    return jsonify({"status": "ok", "service": "whisper"})


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

    result = model.transcribe(wav_path)
    text = result["text"].strip()

    print(f"✅ Transcription: {text}")
    return jsonify({"text": text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)