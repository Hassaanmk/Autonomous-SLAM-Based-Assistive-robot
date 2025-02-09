

# Autonomous SLAM-Based Assistive Robot

## Overview
This project focuses on developing an **Autonomous SLAM-Based Assistive Robot** with navigation and interaction capabilities. The robot is designed to assist users in various environments by utilizing SLAM (Simultaneous Localization and Mapping) and interactive features.

## Features
- **SLAM-based localization** using **RPLIDAR A1**.
- **Navigation** implemented using the **Viam SDK**.
- **Interaction capabilities** using the **Viam OpenAI Integration**.
- **Testing and integration** with **articulated robotics** in **ROS Humble**.
- **Modular and expandable design** for future improvements.

## Project Status
🚧 **Under Development** 🚧
- Currently being tested with **articulated robotics**.
- Continuous improvements in localization and interaction.

## Implementation Details
### Interaction Ability
We leverage the **Viam OpenAI Integration Tutorial** for interactive capabilities:  
🔗 [Viam OpenAI Integration](https://github.com/viam-labs/tutorial-openai-integration/tree/main)

### SLAM and Localization
For localization, we utilize the **RPLIDAR A1** in combination with **Viam's Cartographer resource**:  
🔗 [Viam Cartographer SLAM](https://docs.viam.com/operate/reference/services/slam/cartographer/)

### Navigation
Navigation is implemented using **Viam SDK**:  
🔗 [Viam SDK SLAM Services](https://python.viam.dev/autoapi/viam/services/slam/index.html)

## Hardware Setup
- **Custom Assistive Robot Frame** (Image shown below)
- **RPLIDAR A1** for mapping and localization
- **Embedded computing unit** for real-time processing
- **Sensors and actuators** for interactive movement

## Dependencies
- **Python** (for Viam SDK integration)
- **ROS Humble** (for robotics testing)
- **Viam SDK & APIs**
- **RPLIDAR A1 drivers**

## Installation & Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Hassaanmk/Autonomous-SLAM-Based-Assistive-Robot.git
   cd Autonomous-SLAM-Based-Assistive-Robot
