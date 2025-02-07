import speech_recognition as sr

def test_microphone():
    r = sr.Recognizer()
    r.energy_threshold = 1568
    r.dynamic_energy_threshold = True
    m = sr.Microphone()

    print("Setup complete, listening... Say 'stop' to exit.")

    with m as source:
        r.adjust_for_ambient_noise(source)

        while True:
            print("Please speak into the microphone...")
            try:
                audio = r.listen(source)
                transcript = r.recognize_google(audio, show_all=True)

                if isinstance(transcript, dict) and transcript.get("alternative"):
                    text = transcript["alternative"][0]["transcript"].lower()
                    print("You said:", text)

                    if "stop" in text:
                        print("Stopping...")
                        break
                else:
                    print("No speech detected.")

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
        

if __name__ == "__main__":
    test_microphone()



#def test_microphone():
    r = sr.Recognizer()
    r.energy_threshold = 1568 
    r.dynamic_energy_threshold = True
    m = sr.Microphone()
    print("Setup complete, listening...")
    while True:
        with m as source:
            r.adjust_for_ambient_noise(source) 
            audio = r.listen(source)
    
    transcript = r.recognize_google(audio_data=audio, show_all=True)


    # Initialize recognizer class
    recognizer = sr.Recognizer()

    # Use the default microphone (index 0)
    with sr.Microphone() as source:
        print("Please speak into the microphone...")
        
        # Adjust recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source)

        # Listen for the first phrase
        audio = recognizer.listen(source)

        try:
            # Recognize the speech using Google Web Speech API
            #print("You said: " + recognizer.recognize_google(audio_data=audio, show_all=True))
            transcript = sr.recognize_google(audio_data=audio, show_all=True)
            if type(transcript) is dict and transcript.get("alternative"):
                text = transcript["alternative"][0]["transcript"].lower()
                print(text)
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

#f __name__ == "__main__":
    #test_microphone()
