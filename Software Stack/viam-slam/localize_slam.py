import asyncio
from viam.robot.client import RobotClient
from viam.services.slam import SLAMClient
from viam.services.motion import MotionClient, MotionConfiguration
from viam.proto.common import Pose
from viam.components.base import Base

# Define the connection to the robot
async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  # Replace with actual API key
        api_key_id='x'  # Replace with actual API key ID
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

# Localize using SLAM and move robot using Motion service
async def localize_and_move():
    robot = await connect()
    try:
        # Access the SLAM service (using "Cartographer" as the name of the SLAM service)
        slam = SLAMClient.from_robot(robot, "Cartographer")

        # Get the robot's current position from the SLAM map
        position = await slam.get_position()  # Get position from SLAM service
        print(f"Robot position from SLAM map: {position}")

        # Pose details (x, y, z, theta) might be available in the position response
        pose = Pose(x=position.x, y=position.y, z=0.0, theta=position.theta)
        print(f"Robot pose from SLAM map: {pose}")

        # Initialize the Motion service
        motion = MotionClient.from_robot(robot, "builtin")

        # Get the base component for the robot (typically named 'viam_base')
        base = Base.from_robot(robot, "viam_base")

        # Define a target pose (example, you can adjust it)
        target_pose = Pose(x=3768.0, y=1694.0, z=0.0, theta=1.57)  # Example target pose (x, y, z, theta)

        # Configure Motion settings (optional)
        #motion_configuration = MotionConfiguration()  # Adjust as needed

        # Move robot to the target pose using SLAM
        execution_id = await motion.move_on_map(
            component_name=base.get_resource_name(base),  # Pass the component resource name (base)
            destination=target_pose,                  # Set destination pose
            slam_service_name=slam.get_resource_name(slam),  # Set SLAM service name for localization
              # Optional motion configuration
            timeout=30.0  # Optional timeout in seconds
        )
        print(f"Movement started with execution ID: {execution_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await robot.close()

# Run the localization and movement script
if __name__ == "__main__":
    asyncio.run(localize_and_move())
