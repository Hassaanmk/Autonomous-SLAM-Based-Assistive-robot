import asyncio
from viam.robot.client import RobotClient
from viam.components.camera import Camera

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  
        api_key_id='x'  
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

async def capture_lidar():
    robot = await connect()
    try:
        # Change 'RPLIDAR' to your actual lidar camera name from Viam
        lidar_camera = Camera.from_robot(robot, name="camera-1")  

        # Capture LiDAR image
        image = await lidar_camera.get_image()
        print(f"Received LiDAR image data: {len(image)} bytes")

        # Save the image
        with open("lidar_image.jpg", "wb") as f:
            f.write(image)
        print("Saved LiDAR image as 'lidar_image.jpg'")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await robot.close()

if __name__ == "__main__":
    asyncio.run(capture_lidar())

