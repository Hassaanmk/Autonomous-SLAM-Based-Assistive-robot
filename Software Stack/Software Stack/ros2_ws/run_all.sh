#!/bin/bash

source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 launch my_bot rplidar.launch.py &
ros2 launch my_bot lidar_fov_filter.launch.py &
ros2 launch my_bot online_async_launch.py use_sim_time:=false &
ros2 launch my_bot navigation_launch.py use_sim_time:=false &

wait
