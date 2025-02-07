import random
import asyncio
import re
from gtts import gTTS
import os
import requests  
from groq import Groq
import time
import speech_recognition as sr  
from viam.components.servo import Servo
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from viam.rpc.dial import Credentials, DialOptions 
import params


current_mood = "angry"
style = "abusive"

# Base URL for Groq's LLaMA API endpoint (this is hypothetical and will depend on Groq's actual setup)
os.environ['GROQ_KEY']="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"
MAX_RETRIES = 10

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key=params.viam_api_key,
      api_key_id=params.viam_api_key_id
    )
    return await RobotClient.at_address(params.viam_address, opts)

class LlamaRetriever():
    '''
    Using Llama API from https://console.groq.com/docs/text-chat
    Available models: https://console.groq.com/docs/models 
    '''
    def __init__(self, model='llama3-8b-8192'):
        self.client = Groq(
            api_key=os.environ['GROQ_KEY'],
        )
        self.model = model

    def call_api(self, prompt, system_message):
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]

        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model
                )
                return response.choices[0].message.content

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                attempt += 1
                time.sleep(10)
        print(f"Failed to get chat completion after {MAX_RETRIES} attempts")
        return None

model = LlamaRetriever(model='llama-3.2-3b-preview')

def listen_command():
    """
    Capture audio input from the microphone and convert it to text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand audio")
        return "Sorry, I couldn't understand."
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return "Sorry, I couldn't understand."

def speak_response(text):
    """
    Use gTTS to convert text to speech and play it.
    """
    # Create an audio file from the response text
    tts = gTTS(text=text, lang='en')
    audio_file = "response.mp3"
    tts.save(audio_file)
    
    # Play the audio file
    os.system(f"start {audio_file}")  # For Windows
    # os.system(f"afplay {audio_file}")  # For macOS
    # os.system(f"mpg321 {audio_file}")  # For Linux with mpg321 installed

    #os.remove(audio_file)

def ai_command(command):
    """
    Generate a response quote based on the input command, current mood, and style using LLaMA model from Groq.
    """
    try:
        if command == "I am giving you a command": 
            system_message= "Do as said in prompt"
            prompt= "Say: sure give me the command"
            response_text=model.call_api(prompt,system_message)
            speak_response(response_text) 
            return response_text

        if command == "Sorry, I am feeling tired" or "Sorry, I forgot" or "Never mind, I don't know":
            system_message= "Repeat as said in prompt"
            prompt= command
            response_text=model.call_api(prompt,system_message)
            speak_response(response_text)
            return response_text
        

        # Create the prompt for the LLaMA model
        command_update = f"Answer the question: {command} in {current_mood} and {style} style"
        print(command_update)
        
        # Call the LLaMA model through Groq API
        #response_text = call_llama_groq_api(command_update)

        system_message = '''You are a friend in charge of correctly answering questions.
        '''
        prompt = f'''Question: {command_update}
        '''
        response_text=model.call_api(prompt,system_message)
        if not response_text:
            raise Exception("Empty response from LLaMA API")

        # Use gTTS to vocalize the response
        speak_response(response_text)
        
        return response_text
    
    except Exception as e:
        print(f"Error: {str(e)}")
        errors = ["Sorry, I am feeling tired", "Sorry, I forgot", "Never mind, I don't know"]
        error_message = random.choice(errors)
        
        # Use gTTS to vocalize the error message
        speak_response(error_message)
        
        return error_message

async def loop(robot):
    base = Base.from_robot(robot, 'viam_base')
    r = sr.Recognizer()
    r.energy_threshold = 1568 
    r.dynamic_energy_threshold = True
    m = sr.Microphone()
    #await move_servo("happy")

    print("Setup complete, listening...")
    while True:
        with m as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.listen(source)
            print("Please speak into the microphone...")
        try:
            global current_char
            global current_mood
            global current_person_name
            transcript = r.recognize_google(audio_data=audio, show_all=True)
            if type(transcript) is dict and transcript.get("alternative"):
                text = transcript["alternative"][0]["transcript"].lower()
                print(text)
                if re.search(".*" + params.robot_command_prefix, text):
                    command = re.sub(".*" + params.robot_command_prefix + "\s+",  '', text)
                    print(command)
                    if command == "spin":
                        await base.spin(angle=720, velocity=500)
                    elif command == "turn a little right":
                        await base.spin(angle=-45, velocity=500)
                    elif command == "turn right":
                        await base.spin(angle=-90, velocity=500)
                    elif command == "turn a little left":
                        await base.spin(angle=45, velocity=500)
                    elif command == "turn left":
                        await base.spin(angle=90, velocity=500)
                    elif command == "turn around":
                        await base.spin(angle=180, velocity=500)
                    elif command == "move forward":
                        await base.move_straight(distance=1, velocity=500)
                    elif command == "move backwards":
                        await base.move_straight(distance=-1, velocity=500)
                    elif command == "reset":
                        current_char = ""
                        current_mood = ""
                        current_person_name = ""
                    #elif re.search("^" + '|'.join(params.observe_list), command):
                        #await see_something()
                    #elif command == "act random":
                        #current_char = random.choice(params.char_list.keys())
                        #await say(await ai_command("Say hi " + current_person_name))
                    #elif re.search("^" + params.intro_command, command):
                        #current_person_name = re.sub(params.intro_command, "", command)
                        #await say(await ai_command("Say hi " + current_person_name))
                    #elif re.search("^" + params.char_command +" (" + '|'.join(params.char_list.keys()) + ")", command):
                        #current_char = re.sub(params.char_command, "", command)
                        #await say(await ai_command("Say hi"))
                    #elif re.search("^" + params.char_guess_command +" (" + '|'.join(params.char_list.keys()) + ")", command):
                        #if current_char != "":
                            #char_guess = re.sub(params.char_guess_command, "", command)
                            #print("guess: |" + char_guess + "|actual: |" + current_char + "|")
                            #if char_guess == current_char:
                                #await say(await ai_command("say 'You are correct'"))
                            #else:
                                #await say(await ai_command("say 'You are wrong, try again'"))
                    #elif re.search("^you (seem|look)", command):
                        #current_mood = re.sub("you (seem|look) ", "", command)
                        #asyncio.gather(
                            #await mood_motion(base, current_mood),
                            #await move_servo(current_mood),
                            #await say(await ai_command("Say 'yeah, I am " + current_mood +  "'")),
                        #)
                    else:
                        await speak_response(await ai_command(command))

        except sr.UnknownValueError:
            print("Speech recognition could not understand audio, trying again")
        except Exception as e:
            print("Exception while running loop")
            raise e


# Listen for audio input and then generate the AI response
#user_command = listen_command()
    
#ai_response = ai_command(user_command)

async def main():
    global robot
    robot = await connect()
    print("Connected to robot...")
    try:
        await loop(robot=robot) 
    finally:
        print("Stopping...")
        try:
            await robot.close()
        except asyncio.CancelledError:
            # can be safely ignored
            pass

if __name__ == "__main__":
    asyncio.run(main())

#ai_command("How did your day go?")