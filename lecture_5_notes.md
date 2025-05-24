# Commands for launching project

source /opt/ros/humble/setup.bash
colcon build

W drugim terminalu:

. install/setup.bash

ros2 interface show my_urdf_pkg/action/DrawShape

ros2 action send_goal my_urdf_pkg/action/DrawShape "{time_of_motion: 1.0, shape_to_draw: "square", figure_param:1.2}"


Pozycja poczatkowa:

[0.00, -1.128, -1.279, 0.000]