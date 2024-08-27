import speech_recognition as sr
import pyttsx3
import requests
import json
from gtts import gTTS
import os
import time
from datetime import datetime

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()

# Set verification state and other variables
verification_state = 'name'
max_attempts = 3
attempts = 0

def speak(text, display=True):
    if display:
        print("CONO: " + text)  # Display the text CONO is speaking
    tts = gTTS(text=text, lang='en', slow=False)
    filename = "voice.mp3"
    tts.save(filename)
    os.system(f"mpg123 {filename} >/dev/null 2>&1")  # Suppress output
    os.remove(filename)


def start_recognition():
    global verification_state, attempts

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
        try:
            transcript = recognizer.recognize_google(audio).lower()
            print(f"Recognized: {transcript}")
            handle_transcript(transcript)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you please repeat?", display=False)
        except sr.RequestError:
            speak("There seems to be a network issue. Please try again later.", display=False)

        if verification_state != 'done' and attempts < max_attempts:
            start_recognition()

def handle_transcript(transcript):
    global verification_state, attempts

    if verification_state == 'name':
        if any(name in transcript for name in ['nihal', 'swastik', 'varun','saksham','harshita','nitya']):
            speak("Name verified successfully... say the code to activate me!")
            verification_state = 'code'
        else:
            attempts += 1
            if attempts < max_attempts:
                speak("It's not a valid name. Say your name again.")
            else:
                speak("Please try again, you have reached your limit. You can access later!")

    elif verification_state == 'code':
        if 'hello world' in transcript:
            speak("Code verification is successfully completed")
            verification_state = 'done'
            cono_will_wish()
        else:
            attempts += 1
            if attempts < max_attempts:
                speak("Code invalid... say the code again.")
            else:
                speak("Please try again, you have reached your limit. You can access later!")

    elif verification_state == 'done':
        openai_response = fetch_openai_response(transcript)
        speak(openai_response)

def cono_will_wish():
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning Sir."
    elif 12 <= hour < 18:
        greeting = "Good Afternoon Sir."
    else:
        greeting = "Good Evening Sir."

    speak(greeting)
    speak("I'm CONO, your AI assistant, tell me how can I assist you today?")
    start_recognition()

def fetch_openai_response(prompt):
    response = requests.post('http://localhost:3000/api/openai', json={"prompt": prompt})
    data = response.json()
    return data['choices'][0]['text'].strip()

# Initial prompt to start the interaction
speak("I'm CONO... say your name for verification...")
start_recognition()
