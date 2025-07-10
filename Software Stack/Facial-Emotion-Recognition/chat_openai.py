import os
import speech_recognition as sr
import pyttsx3
from openai import AzureOpenAI
import sys
import time

sys.stderr = open(os.devnull, 'w')  # Suppress ALSA stderr output
# Azure OpenAI Configuration
endpoint = "x"
model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"
subscription_key = "x"
api_version = "x"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Adjust this as needed (default ~200)

# Initialize recognizer
recognizer = sr.Recognizer()


# Conversation history
conversation = [
    {"role": "system", "content": "You are a helpful assistant.give precise and to the point answers as a human interaction"}
]

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        time.sleep(5)
        audio = recognizer.listen(source, phrase_time_limit=5)
        #audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "I didn't catch that. Please repeat."
        except sr.RequestError:
            return "Sorry, speech service is unavailable."

def chat(user_input):
    conversation.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        messages=conversation,
        max_tokens=1024,
        temperature=1.0,
        top_p=1.0,
        model=deployment
    )
    reply = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": reply})
    return reply

# Main loop
speak("Hello! I'm your voice assistant. What would you like to talk about?")
while True:
    user_input = listen()
    print("You said:", user_input)

    if "goodbye" in user_input.lower():
        speak("Goodbye! Have a great day.")
        break

    reply = chat(user_input)
    print("Assistant:", reply)
    speak(reply)