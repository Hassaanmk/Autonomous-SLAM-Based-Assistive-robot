import asyncio
from viam.robot.client import RobotClient
from viam.services.motion import MotionClient
from viam.components.base import Base
from viam.services.slam import SLAMClient
from viam.proto.common import Pose

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  # Replace with your actual API key
        api_key_id='x'  # Replace with your actual API key ID
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

async def move_robot():
    robot = await connect()

    try:
        # Initialize Motion and SLAM clients
        motion = MotionClient.from_robot(robot, name="builtin")
        base = Base.from_robot(robot, name="viam_base")
        slam = SLAMClient.from_robot(robot, name="Cartographer")

        # Define a target pose (adjust x, y, z, orientation as needed)
        target_pose = Pose(x=1.0, y=2.0, z=0.0, theta=0.0)

        # Get correct resource names
        base_resource_name = Base.get_resource_name("viam_base")
        slam_service_name = SLAMClient.get_resource_name("Cartographer")

        # Move robot using SLAM map
        execution_id = await motion.move_on_map(
            component_name=base_resource_name,
            destination=target_pose,
            slam_service_name=slam_service_name
        )

        print(f"Movement started with execution ID: {execution_id}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Ensure robot connection is closed
        await robot.close()

if __name__ == "__main__":
    asyncio.run(move_robot())
