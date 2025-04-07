import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rivial/Desktop/ROS2/ros2_ws/src/install/learning_tf2_py'
