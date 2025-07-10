import sys
import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from functools import partial
import threading

class NavClient(Node):
    def __init__(self):
        super().__init__('simple_nav_gui')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, goal_coords):
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('NavigateToPose action server not available!')
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(goal_coords)

        self._action_client.send_goal_async(goal_msg)

    def create_pose(self, coords):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = coords['x']
        pose.pose.position.y = coords['y']
        pose.pose.position.z = 0.0

        quat = quaternion_from_euler(0, 0, coords['theta'])
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]

        return pose

class NavGUI(QWidget):
    def __init__(self, nav_client):
        super().__init__()
        self.nav_client = nav_client
        self.setWindowTitle('Simple Nav2 GUI')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        # Define buttons and goals
        HASSAAN_GOAL = {'x': 2.7249138355255127, 'y': -0.9860003590583801, 'theta': -1.89}
        RAFEY_GOAL = {'x': 1.9673306941986084, 'y': 3.070401668548584, 'theta': 2.81}

        # Create buttons
        self.hassaan_button = QPushButton('Hassaan', self)
        self.hassaan_button.clicked.connect(partial(self.nav_client.send_goal, HASSAAN_GOAL))

        self.rafey_button = QPushButton('Rafey', self)
        self.rafey_button.clicked.connect(partial(self.nav_client.send_goal, RAFEY_GOAL))

        # Add buttons to layout
        layout.addWidget(self.hassaan_button)
        layout.addWidget(self.rafey_button)

        self.setLayout(layout)

def run_gui(nav_client):
    app = QApplication(sys.argv)
    window = NavGUI(nav_client)
    window.show()
    sys.exit(app.exec_())

def main():
    rclpy.init()
    nav_client = NavClient()

    # Run GUI in a separate thread so ROS2 and the GUI can run simultaneously
    gui_thread = threading.Thread(target=run_gui, args=(nav_client,))
    gui_thread.start()

    # Keep spinning ROS2 node
    rclpy.spin(nav_client)
    nav_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
