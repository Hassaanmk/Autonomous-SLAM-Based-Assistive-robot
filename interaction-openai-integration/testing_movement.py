import asyncio
import speech_recognition as sr
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
import params  # Ensure params.py has your Viam API credentials

# Function to connect to the robot
async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key=params.viam_api_key,
        api_key_id=params.viam_api_key_id
    )
    return await RobotClient.at_address(params.viam_address, opts)

# Function to move the robot based on voice commands
async def voice_control_base(robot):
    base = Base.from_robot(robot, 'viam_base')
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Voice control activated. Say a command (forward, backward, left, right, stop)...")

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")

            if "forward" in command:
                print("Moving forward...")
                await base.move_straight(distance=500, velocity=200)

            elif "backward" in command:
                print("Moving backward...")
                await base.move_straight(distance=-500, velocity=200)

            elif "left" in command:
                print("Turning left...")
                await base.spin(angle=90, velocity=200)

            elif "right" in command:
                print("Turning right...")
                await base.spin(angle=-90, velocity=200)

            elif "stop" in command:
                print("Stopping robot...")
                break  # Exit the loop

            else:
                print("Unknown command. Please say forward, backward, left, right, or stop.")

        except sr.UnknownValueError:
            print("Could not understand, please repeat.")
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")

async def main():
    robot = await connect()
    print("Connected to robot...")
    try:
        await voice_control_base(robot)
    finally:
        print("Stopping...")
        await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
