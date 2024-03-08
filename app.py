# from flask import Flask, render_template, request
# import speech_recognition as sr

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/translate', methods=['POST'])
# def translate():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening...")
#         audio = recognizer.listen(source)

#     try:
#         text = recognizer.recognize_google(audio)
#         return text
#     except sr.UnknownValueError:
#         return "Could not understand audio"
#     except sr.RequestError as e:
#         return "Error: {0}".format(e)

# if __name__ == '__main__':
#     app.run(debug=True)



import pyaudio
import wave
import os
from googletrans import Translator
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    translator = Translator()
    
    # Define audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "input.wav"
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save audio to file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    # Use Google Translate to translate audio to the desired language
    try:
        translated_text = translator.translate(os.system(f"ffmpeg -i input.wav -vn -ar 44100 -ac 2 -b:a 192k -f mp3 output.mp3"), dest=request.json['language']).text
        print(translated_text)
        return jsonify({'translation': translated_text})
    except Exception as e:
        return jsonify({'error': f"Error: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
