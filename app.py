from flask import Flask, render_template, request, jsonify
import googletrans
import speech_recognition as sr
import gtts
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import wave
import time
import threading

app = Flask(__name__)

# Global variables to track recording state and translated speech
recording = False
translated_audio = None
translated_text = ''

# Function to start recording
def start_recording(language):
    global recording
    global translated_audio
    global translated_text

    recording = True

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "input.wav"

    audio = pyaudio.PyAudio()

    # Open the stream
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    # Record audio data from the stream until recording is stopped
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording complete.")

    # Stop the stream and close it
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio data to a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Load the recorded audio file
    audio_file = "input.wav"
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    # Recognize the speech from the audio data
    try:
        text = recognizer.recognize_google(audio_data, language="en")
        print("Recognized text:", text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        text = ""
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        text = ""
        
        
    # Translate the recognized text to the target language
    translator = googletrans.Translator()
    translation = translator.translate(text, dest=language)
    translated_text = translation.text
    print("Translated text:", translation.text)

    # Convert the translated text to speech
    translated_audio = gtts.gTTS(translation.text, lang=language)

# Route to start recording
@app.route('/start-recording', methods=['POST'])
def start_recording_route():
    global recording
    if not recording:
        language = request.json.get('language', 'en')
        recording_thread = threading.Thread(target=start_recording, args=(language,))
        recording_thread.start()
    return jsonify({'message': 'Recording started'})

# Route to stop recording
@app.route('/stop-recording', methods=['POST'])
def stop_recording_route():
    global recording
    recording = False
    return jsonify({'message': 'Recording stopped'})

# Route to play translated speech
@app.route('/play-translated-speech', methods=['POST'])
def play_translated_speech():
    global translated_audio
    if translated_audio:
        translated_audio.save("translated_audio.mp3")
        audio = AudioSegment.from_mp3("translated_audio.mp3")
        play(audio)
        return jsonify({'message': 'Translated speech played', 'translated_text': translated_text})
    else:
        return jsonify({'error': 'Translated speech not available'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)










# from flask import Flask, render_template, request, jsonify
# import googletrans
# import speech_recognition as sr
# import gtts
# from pydub import AudioSegment
# from pydub.playback import play
# import pyaudio
# import wave

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/translate', methods=['POST'])
# def translate():
#     input_lang = "en"
#     output_lang = request.json['language']
#     recognizer = sr.Recognizer()

#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 44100
#     CHUNK = 1024
#     RECORD_SECONDS = 5
#     WAVE_OUTPUT_FILENAME = "input.wav"

#     audio = pyaudio.PyAudio()

#     # Open the stream
#     stream = audio.open(format=FORMAT,
#                         channels=CHANNELS,
#                         rate=RATE,
#                         input=True,
#                         frames_per_buffer=CHUNK)

#     print("Speak now...")

#     frames = []

#     # Record audio data from the stream
#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     print("Recording complete.")

#     # Stop the stream and close it
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     # Save the recorded audio data to a WAV file
#     with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))

#     # Load the recorded audio file
#     audio_file = "input.wav"
#     with sr.AudioFile(audio_file) as source:
#         audio_data = recognizer.record(source)

#     # Recognize the speech from the audio data
#     try:
#         text = recognizer.recognize_google(audio_data, language=input_lang)
#         print("Recognized text:", text)
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand the audio")
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))

#     # Translate the recognized text to the target language
#     translator = googletrans.Translator()
#     translation = translator.translate(text, dest=output_lang)
#     print("Translated text:", translation.text)

#     # Convert the translated text to speech
#     converted_audio = gtts.gTTS(translation.text, lang=output_lang)

#     # Save the translated text to an audio file
#     translated_audio_file = "translated_audio.mp3"
#     converted_audio.save(translated_audio_file)

#     # Load the translated audio file and play it
#     audio = AudioSegment.from_mp3(translated_audio_file)
#     play(audio)

#     return jsonify({'translation': translation.text})

#     # recognizer = sr.Recognizer()
#     # translator = Translator()
    
#     # with sr.Microphone() as source:
#     #     print("Speak something...")
#     #     audio = recognizer.listen(source)
    
#     # try:
#     #     text = recognizer.recognize_google(audio)
#     #     translated_text = translator.translate(text, dest=request.json['language']).text
#     #     return jsonify({'translation': translated_text})
#     # except sr.UnknownValueError:
#     #     return jsonify({'error': 'Could not understand audio'})
#     # except sr.RequestError as e:
#     #     return jsonify({'error': f"Could not request results: {e}"})

# if __name__ == '__main__':
#     app.run(debug=True)
