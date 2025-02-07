import asyncio
import speech_recognition as sr
from viam.components.base import Base
from viam.robot.client import RobotClient
import params  # Ensure params.py has your Viam API credentials

# Global variables to track movement state
is_moving = False
stop_command_received = False

# Function to connect to the robot
async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key=params.viam_api_key,
        api_key_id=params.viam_api_key_id
    )
    return await RobotClient.at_address(params.viam_address, opts)

# Movement function
async def move_robot(base, direction="forward"):
    global is_moving, stop_command_received
    
    is_moving = True
    stop_command_received = False

    try:
        if direction == "forward":
            print("Moving forward...")
            await base.move_straight(distance=500, velocity=200)
        elif direction == "backward":
            print("Moving backward...")
            await base.move_straight(distance=-500, velocity=200)
        elif direction == "left":
            print("Turning left...")
            await base.spin(angle=90, velocity=100)
        elif direction == "right":
            print("Turning right...")
            await base.spin(angle=-90, velocity=100)
        
        # Keep checking for stop command while the robot is moving
        while is_moving and not stop_command_received:
            await asyncio.sleep(0.1)  # Check for stop command periodically
    finally:
        is_moving = False
        if stop_command_received:
            print("Movement stopped due to stop command.")
            await base.move_straight(distance=0, velocity=0)  # Stop the robot

# Listen to voice commands
async def listen_for_commands(base):
    global stop_command_received
    
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            print("Listening for commands...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            
            if "stop" in command:
                stop_command_received = True
                print("Stop command received")
            elif "forward" in command:
                await move_robot(base, "forward")
            elif "backward" in command:
                await move_robot(base, "backward")
            elif "left" in command:
                await move_robot(base, "left")
            elif "right" in command:
                await move_robot(base, "right")
            else:
                print("Command not recognized")

        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")

# Set up the robot and components
async def setup_robot():
    robot = await connect()
    print("Connected to robot...")
    base = await robot.get_component('base')  # Access the robot base component (no need to specify Base)
    return base


# Main function to run the robot control
async def main():
    base = await setup_robot()
    
    # Start the listening for voice commands
    await listen_for_commands(base)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
