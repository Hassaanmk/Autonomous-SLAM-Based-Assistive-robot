import asyncio
from viam.robot.client import RobotClient
from viam.components.movement_sensor import MovementSensor

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='x',  
        api_key_id='x'  
    )
    robot = await RobotClient.at_address('x', opts)
    return robot

async def get_imu_readings():
    robot = await connect()
    try:
        # Access IMU sensor
        imu = MovementSensor.from_robot(robot, "imu")  # Replace with correct name if different

        # Get linear acceleration
        acceleration = await imu.get_linear_acceleration()
        print(f"📊 Linear Acceleration: {acceleration}")

        # Get angular velocity
        angular_velocity = await imu.get_angular_velocity()
        print(f"🔄 Angular Velocity: {angular_velocity}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await robot.close()

if __name__ == "__main__":
    asyncio.run(get_imu_readings())
