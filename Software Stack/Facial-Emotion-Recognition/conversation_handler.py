import random
import time
from datetime import datetime

class ConversationHandler:
    def __init__(self, speak_fn, listen_fn, llama_fn):
        self.speak = speak_fn
        self.listen = listen_fn
        self.llama = llama_fn
        self.last_user_input = None
        self.last_detected = time.time()
        self.cooldown_time = 10
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

    def get_time_based_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning! How can I help?"
        elif hour < 18:
            return "Good afternoon! Need something?"
        else:
            return "Good evening! What can I do for you?"

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
            print(f"[User Input]: {user_input}")  # Debug print

            if user_input:
                if any(phrase in user_input.lower() for phrase in self.end_chat):
                    self.speak("Alright, have a great day! Goodbye!")
                    return True  # Signal to exit

                if user_input != self.last_user_input:
                    response = self.llama(user_input)
                    self.speak(response)
                    self.last_user_input = user_input
                else:
                    self.speak("You just asked that. Anything else on your mind?")
        return False  # Continue running
