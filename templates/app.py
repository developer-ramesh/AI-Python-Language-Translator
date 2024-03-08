import googletrans
import speech_recognition as sr
import gtts
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import wave

input_lang = "en"
output_lang = "bn"
recognizer = sr.Recognizer()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "input.wav"

audio = pyaudio.PyAudio()

# Open the stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("Speak now...")

frames = []

# Record audio data from the stream
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
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
with sr.AudioFile(audio_file) as source:
    audio_data = recognizer.record(source)

# Recognize the speech from the audio data
try:
    text = recognizer.recognize_google(audio_data, language=input_lang)
    print("Recognized text:", text)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Translate the recognized text to the target language
translator = googletrans.Translator()
translation = translator.translate(text, dest=output_lang)
print("Translated text:", translation.text)

# Convert the translated text to speech
converted_audio = gtts.gTTS(translation.text, lang=output_lang)

# Save the translated text to an audio file
translated_audio_file = "translated_audio.mp3"
converted_audio.save(translated_audio_file)

# Load the translated audio file and play it
audio = AudioSegment.from_mp3(translated_audio_file)
play(audio)
