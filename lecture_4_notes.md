# Commands for launching project

source /opt/ros/humble/setup.bash
colcon build

W drugim terminalu:

. install/setup.bash
ros2 launch my_urdf_pkg display.launch.py

colcon build --packages-select my_urdf_pkg


