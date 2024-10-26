from flask import Flask, render_template, request, jsonify, send_file
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import logging
import os

app = Flask(__name__)

# Initialize speech recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    app.logger.debug(f"Audio file received: {audio_file.filename}")

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio)
            app.logger.debug(f"Recognized text: {recognized_text}")
    except sr.UnknownValueError:
        return jsonify({"error": "Speech recognition failed"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Error with the recognition service: {str(e)}"}), 500

    target_language = request.form.get('language')
    if not target_language:
        return jsonify({"error": "Target language not specified"}), 400

    app.logger.debug(f"Received target language: {target_language}")

    try:
        translation = translator.translate(recognized_text, dest=target_language)
        translated_text = translation.text
        app.logger.debug(f"Translated text: {translated_text}")

        # Check if TTS is enabled
        enable_tts = request.form.get('enable_tts', 'false').lower() == 'true'
        audio_url = None

        if enable_tts:
            tts = gTTS(translated_text, lang=target_language)
            audio_path = "static/tts_output.mp3"
            tts.save(audio_path)
            audio_url = f"/static/tts_output.mp3"

        return jsonify({
            "translated_text": translated_text,
            "audio_url": audio_url
        }), 200
    except Exception as e:
        app.logger.debug(f"Translation or TTS error: {str(e)}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
