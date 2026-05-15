from flask import Flask, request, jsonify, send_from_directory, send_file
from groq import Groq
import json
import os
import subprocess
import requests
from datetime import datetime

app = Flask(__name__, static_folder=".")

UPLOAD_FOLDER = "audios"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

# ─────────────── HELPERS ───────────────
def load_records():
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/records?order=id.asc",
        headers=supabase_headers()
    )
    return res.json() if res.ok else []

def save_record(text):
    record = {
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "heure": datetime.now().strftime("%H:%M:%S"),
    }
    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/records",
        headers={**supabase_headers(), "Prefer": "return=representation"},
        json=record
    )
    return res.json()[0] if res.ok else record

def delete_record_db(record_id):
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/records?id=eq.{record_id}",
        headers=supabase_headers()
    )

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

# ─────────────── PAGE HTML ───────────────
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# ─────────────── UPLOAD AUDIO ───────────────
@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["audio"]
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    webm_path = os.path.join(UPLOAD_FOLDER, f"audio_{now}.webm")
    wav_path  = os.path.join(UPLOAD_FOLDER, f"audio_{now}.wav")

    file.save(webm_path)

    if not convert_to_wav(webm_path, wav_path):
        return jsonify({"error": "Conversion audio échouée"}), 500

    try:
        with open(wav_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        print(f"✅ Transcription: {text}")
    except Exception as e:
        print("Erreur Groq Whisper:", str(e))
        return jsonify({"error": "Transcription échouée"}), 500

    if not text:
        return jsonify({"error": "Transcription vide"}), 500

    record = save_record(text)
    return jsonify({"text": text, "record": record})

# ─────────────── HISTORIQUE ───────────────
@app.route("/api/records")
def get_records():
    records = load_records()
    return jsonify({"total": len(records), "records": records})

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    delete_record_db(record_id)
    return jsonify({"message": "Supprimé ✅"})

# ─────────────── EXPORT ───────────────
@app.route("/api/export")
def export():
    records = load_records()
    lines = [f"{r['date']} {r['heure']} : {r['text']}" for r in records]
    with open("records.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return send_file(os.path.abspath("records.txt"), as_attachment=True)

# ─────────────── RUN ───────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
