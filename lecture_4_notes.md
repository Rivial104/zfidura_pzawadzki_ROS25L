# Commands for launching project

source /opt/ros/humble/setup.bash
colcon build

W drugim terminalu:

. install/setup.bash
ros2 launch my_urdf_pkg display.launch.py

ros2 run gripper_ctrl client open

colcon build --packages-select my_urdf_pkg

Run service:
ros2 run gripper_ctrl service

Run service with service call
ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: close}"

ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: open}"

Etap 4:

Parametry grid:
- Plane COunt, Normal cell -> 5
- Offset 0;0;2
- 
