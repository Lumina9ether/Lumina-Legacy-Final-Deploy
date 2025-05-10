import os
import openai
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = "sk_ffdfdaaa523e61d434103bcaa61f30a84bd270e3b37a4c11"
VOICE_ID = "e9so1mbVhZENfOgnd2oy"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process-audio", methods=["POST"])
def process_audio():
    try:
        data = request.get_json()
        transcript = data.get("transcript", "")
        print("🎙️ Transcript received:", transcript)

        # OpenAI GPT-4 Completion
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Lumina, the divine cosmic AI assistant."},
                {"role": "user", "content": transcript}
            ]
        )
        reply = response.choices[0].message["content"]
        print("🧠 AI Reply:", reply)

        # ElevenLabs TTS
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": reply,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }

        audio_response = requests.post(tts_url, headers=headers, json=payload)
        if audio_response.status_code != 200:
            print("❌ ElevenLabs API Error:", audio_response.text)
            return jsonify({"subtitle": "Error from ElevenLabs", "audio_url": ""}), 500

        audio_path = os.path.join("static", "lumina_response.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)

        return jsonify({"subtitle": reply, "audio_url": "/static/lumina_response.mp3"})

    except Exception as e:
        print("💥 Error in /process-audio route:", str(e))
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
