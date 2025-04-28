# Commands for launching project

source /opt/ros/humble/setup.bash
colcon build

W drugim terminalu:

. install/setup.bash
ros2 launch my_urdf_pkg display.launch.py

ros2 run gripper_ctrl control_gripper open

colcon build --packages-select my_urdf_pkg


