from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import googletrans
import os
import gtts
from datetime import datetime

app = Flask(__name__)

# Function to process audio file
def process_audio(audio_file, output_file , input_lang, output_lang):
    recognizer = sr.Recognizer()

    # Perform speech recognition and translation on the WAV audio file 
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    try:
        # Perform speech recognition
        recognized_text = recognizer.recognize_google(audio_data, language=input_lang)
        print("Recognized text:", recognized_text)
        
        # Translate the recognized text to the target language
        translator = googletrans.Translator()
        translated_text = translator.translate(recognized_text, dest=output_lang).text
        print("Translated text:", translated_text)
        
        # Convert the translated text to speech
        translated_audio = gtts.gTTS(translated_text, lang=output_lang)
        translated_audio.save(output_file)
        
        return translated_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio_data' in request.files:
        audio_file = request.files['audio_data']

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Generate new filename with timestamp
        if audio_file.filename.endswith('.wav'):
            new_filename = f'static/recorded_audio_{timestamp}.wav'
        else:
            new_filename = f'static/recorded_audio_{timestamp}.mp3'

        # Save the audio file with the new filename
        audio_file.save(new_filename)

        # If the file is not in WAV format, convert it to WAV using ffmpeg
        if not audio_file.filename.endswith('.wav'):
            converted_filename = f'static/converted_audio_{timestamp}.wav'
            os.system(f"ffmpeg -i {new_filename} -acodec pcm_u8 -ar 22050 {converted_filename}")
            
        # get converted audio file with absolute path
        if os.path.exists(converted_filename):
            file = os.path.abspath(converted_filename)
        
        translated_file = f'static/translated_audio_{timestamp}.mp3'
        # Process the audio file
        translated_text = process_audio(file ,translated_file ,request.form['input_language'], request.form['output_language'])
        
        # get converted audio file with absolute path
        if os.path.exists(translated_file):
            file = translated_file
            
        if translated_text:
            return jsonify({'message': 'Audio file processed successfully', 'translated_text': translated_text, 'audio_file':file})
        else:
            return jsonify({'error': 'Error processing audio'})

    return jsonify({'error': 'No audio data received'})


@app.route('/')
def index():
    print(googletrans.LANGUAGES)
    return render_template('index.html')


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)









# ## Using server side recording *************************
# from flask import Flask, render_template, request, jsonify
# import googletrans
# import speech_recognition as sr
# import gtts
# from pydub import AudioSegment
# from pydub.playback import play
# import pyaudio
# import wave
# import time
# import threading

# app = Flask(__name__)

# # Global variables to track recording state and translated speech
# recording = False
# translated_audio = None
# translated_text = ''

# # Function to start recording
# def start_recording(language):
#     global recording
#     global translated_audio
#     global translated_text

#     recording = True

#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 44100
#     CHUNK = 1024
#     WAVE_OUTPUT_FILENAME = "input.wav"

#     audio = pyaudio.PyAudio()

#     # Open the stream
#     stream = audio.open(format=FORMAT,
#                         channels=CHANNELS,
#                         rate=RATE,
#                         input=True,
#                         frames_per_buffer=CHUNK)

#     print("Recording...")

#     frames = []

#     # Record audio data from the stream until recording is stopped
#     while recording:
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
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_file) as source:
#         audio_data = recognizer.record(source)

#     # Recognize the speech from the audio data
#     try:
#         text = recognizer.recognize_google(audio_data, language="en")
#         print("Recognized text:", text)
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand the audio")
#         text = ""
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))
#         text = ""
        
        
#     # Translate the recognized text to the target language
#     translator = googletrans.Translator()
#     translation = translator.translate(text, dest=language)
#     translated_text = translation.text
#     print("Translated text:", translation.text)

#     # Convert the translated text to speech
#     translated_audio = gtts.gTTS(translation.text, lang=language)

# # Route to start recording
# @app.route('/start-recording', methods=['POST'])
# def start_recording_route():
#     global recording
#     if not recording:
#         language = request.json.get('language', 'en')
#         recording_thread = threading.Thread(target=start_recording, args=(language,))
#         recording_thread.start()
#     return jsonify({'message': 'Recording started'})

# # Route to stop recording
# @app.route('/stop-recording', methods=['POST'])
# def stop_recording_route():
#     global recording
#     recording = False
#     return jsonify({'message': 'Recording stopped'})

# # Route to play translated speech
# @app.route('/play-translated-speech', methods=['POST'])
# def play_translated_speech():
#     global translated_audio
#     if translated_audio:
#         translated_audio.save("translated_audio.mp3")
#         audio = AudioSegment.from_mp3("translated_audio.mp3")
#         play(audio)
#         return jsonify({'message': 'Translated speech played', 'translated_text': translated_text})
#     else:
#         return jsonify({'error': 'Translated speech not available'})

# @app.route('/')
# def index():
#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
