from flask import Flask, render_template, request, send_file
import os
import io
import base64
from gtts import gTTS

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

LANGUAGES = {
    "id": "Indonesia",
    "en": "English",
    "ms": "Melayu",
    "ar": "Arab",
    "zh-CN": "China",
    "ja": "Jepang",
    "ko": "Korea",
    "fr": "Perancis",
    "de": "Jerman",
    "es": "Spanyol",
    "hi": "Hindi",
    "pt": "Portugis",
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    text = ""
    lang = "id"
    slow = False

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        lang = request.form.get("lang", "id")
        slow = request.form.get("slow") == "true"

        if not text:
            error = "Mohon masukkan teks terlebih dahulu."
        elif len(text) > 5000:
            error = "Teks terlalu panjang. Maksimal 5000 karakter."
        else:
            try:
                tts = gTTS(text=text, lang=lang, slow=slow)
                buffer = io.BytesIO()
                tts.write_to_fp(buffer)
                buffer.seek(0)
                audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                result = {
                    "audio": audio_base64,
                    "text": text,
                    "lang": lang,
                    "lang_name": LANGUAGES.get(lang, lang)
                }
            except Exception as e:
                print(f"TTS error: {e}")
                error = "Gagal mengkonversi teks. Coba lagi."

    return render_template("index.html", result=result, error=error,
                           text=text, lang=lang, slow=slow, languages=LANGUAGES)

@app.route("/download", methods=["POST"])
def download():
    audio_data = request.form.get("audio_data")
    if not audio_data:
        return "Invalid", 400
    try:
        audio_bytes = base64.b64decode(audio_data)
        buffer = io.BytesIO(audio_bytes)
        return send_file(buffer, mimetype="audio/mpeg",
                         as_attachment=True, download_name="TextToSpeech.mp3")
    except Exception as e:
        print(f"Download error: {e}")
        return "Error", 500

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

if __name__ == "__main__":
    app.run(debug=True)
