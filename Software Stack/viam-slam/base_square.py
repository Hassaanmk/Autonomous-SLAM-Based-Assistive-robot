import asyncio
from viam.robot.client import RobotClient
from viam.components.sensor import Sensor
from viam.components.camera import Camera
import asyncio

from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  
        api_key_id='x'  
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

async def moveInSquare(base):
    for _ in range(4):
        # moves the rover forward 500mm at 500mm/s
        # spins the rover 90 degrees at 100 degrees per second
        await base.spin(velocity=100, angle=90)
        print("spin 90 degrees")

async def main():
    robot = await connect()

    roverBase = Base.from_robot(robot, 'viam_base')

    # Move the rover in a square
    await moveInSquare(roverBase)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())