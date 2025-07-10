import asyncio
from viam.robot.client import RobotClient
from viam.components.sensor import Sensor
from viam.components.camera import Camera

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  
        api_key_id='x'  
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

async def check_components():
    robot = await connect()
    try:
        # Print all available components
        print("🔹 Available components:", robot.resource_names)

    finally:
        await robot.close()

if __name__ == "__main__":
    asyncio.run(check_components())
