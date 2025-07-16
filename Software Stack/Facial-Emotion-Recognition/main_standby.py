import os
import sys
import time
import random
import pyttsx3
import speech_recognition as sr
from openai import AzureOpenAI
import sounddevice as sd

# Suppress ALSA errors
sys.stderr = open(os.devnull, 'w')

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

# TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Speech recognition
recognizer = sr.Recognizer()

# Conversation history
conversation = [
    {"role": "system", "content": "You are a helpful assistant. Give precise and to-the-point answers as in a human interaction."}
]

# Speak function
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# Listen function
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Speech not recognized.")
            return None
        except sr.RequestError:
            print("Google Speech API is unavailable.")
            return None
        except Exception as e:
            print(f"Microphone error: {e}")
            return None

# Azure GPT call
def azure_call(prompt):
    conversation.append({"role": "user", "content": prompt})
    try:
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
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "I'm having trouble connecting to the server."

# ConversationHandler class
class ConversationHandler:
    def __init__(self, speak_fn, listen_fn, llama_fn):
        self.speak = speak_fn
        self.listen = listen_fn
        self.llama = llama_fn
        self.last_user_input = None
        self.cooldown_time = 10
        self.last_detected = time.time()
        self.conversation_started = False

        self.greetings = [
            "Hey there! Need something?",
            "Good to see you! How can I assist?",
            "Hi! What brings you here?",
            "Welcome back! Anything I can do for you?",
            "Hey! Looking for help?",
            "Hello again! How may I assist you today?",
            "Hi! What can I help you with?",
            "Hey! Feel free to ask anything.",
            "Nice to see you! How can I support you today?",
            "Hi there! Ready when you are."
        ]

        self.continue_chat = [
            "Still around? Need anything else?",
            "Do you have any more questions?",
            "If you have more questions, you can ask me.",
            "Anything else I can help with?",
            "Let me know if there’s something on your mind.",
            "I'm here if you need more help.",
            "Don't hesitate to ask more!",
            "You can ask me anything else if you'd like."
        ]

        self.end_chat = [
            "i don't have any more questions thanks",
            "that's all",
            "i'm done",
            "no more questions",
            "bye",
            "goodbye",
            "exit",
            "quit",
            "stop",
            "see you",
            "that's it"
        ]

    def handle_interaction(self):
        current_time = time.time()
        if current_time - self.last_detected > self.cooldown_time:
            self.last_detected = current_time

            if not self.conversation_started:
                greeting = random.choice(self.greetings)
                self.speak(greeting)
                self.conversation_started = True
            else:
                chat_more = random.choice(self.continue_chat)
                self.speak(chat_more)

            user_input = self.listen()
            print(f"[User Input]: {user_input}")

            if user_input:
                if any(phrase in user_input.lower() for phrase in self.end_chat):
                    self.speak("Alright, have a great day! Goodbye!")
                    return True  # Enter standby
                if user_input != self.last_user_input:
                    response = self.llama(user_input)
                    print("response from gpt: ", response)
                    self.speak(response)
                    self.last_user_input = user_input
                else:
                    self.speak("You just asked that. Anything else on your mind?")
        return False

    def enter_standby(self):
        self.conversation_started = False  # Reset conversation flag
        standby_duration = 30
        standby_start = time.time()

        self.speak("I'll wait here. Just say 'hello' when you need me again.")
        while time.time() - standby_start < standby_duration:
            print("[STANDBY] Listening for wake word ('hello' or 'hi')...")
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, phrase_time_limit=3)
                    wake_phrase = recognizer.recognize_google(audio)
                    print(f"[STANDBY] Heard: {wake_phrase}")
                    if any(greet in wake_phrase.lower() for greet in ["hello", "hi"]):
                        self.speak("Hey again! How can I help?")
                        self.last_user_input = None  # Reset history
                        return  # Exit standby
            except Exception as e:
                print(f"[STANDBY ERROR] {e}")
            time.sleep(1)  # Avoid busy looping
        self.speak("Going silent for now. Call me when you need me.")

# Instantiate handler
conv = ConversationHandler(
    speak_fn=speak,
    listen_fn=listen,
    llama_fn=azure_call
)

# Main loop
def main():
    print("[INFO] Starting main loop...")
    while True:
        #print("[INFO] Running interaction handler...")
        should_enter_standby = conv.handle_interaction()
        #print(f"[INFO] Handler returned: {should_enter_standby}")
        if should_enter_standby:
            print("[INFO] Entering standby mode...")
            conv.enter_standby()

if __name__ == "__main__":
    main()



