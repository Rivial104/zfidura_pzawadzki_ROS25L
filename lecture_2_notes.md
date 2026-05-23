# Lecture 2 - projekt 1

Pakiet: `pose_subscriber`

```text
pose_sub  - wypisuje pozycje zolwia z /turtle1/pose
auto_p    - rysuje litere P albo K
```

## Utworzenie pakietu od zera

```bash
mkdir -p ~/ros2_ws/src
ros2 pkg create --build-type ament_python --destination-directory ~/ros2_ws/src pose_subscriber --dependencies rclpy turtlesim geometry_msgs std_msgs
```

## Build

```bash
colcon build --packages-select pose_subscriber
ros2 pkg executables pose_subscriber
```

## Etap 1 - pozycja zolwia

Terminal 1:

```bash
ros2 run turtlesim turtlesim_node
```

Terminal 2:

```bash
ros2 run turtlesim turtle_teleop_key
```

Terminal 3:

```bash
ros2 topic list
ros2 topic info /turtle1/pose
ros2 interface show turtlesim/msg/Pose
```

Wazne:

```text
/turtle1/pose -> turtlesim/msg/Pose
```

Struktura `Pose`:

```text
float32 x
float32 y
float32 theta
float32 linear_velocity
float32 angular_velocity
```

Uruchomienie subskrybera:

```bash
ros2 run pose_subscriber pose_sub
```

Oczekiwany log:

```text
I am currently at x=<pozycja_x> and y=<pozycja_y>.
```

## Etap 2 - predkosc i litera P

Przy uruchomionym `turtlesim_node`:

```bash
ros2 node info /turtlesim
ros2 topic info /turtle1/cmd_vel
ros2 interface show geometry_msgs/msg/Twist
```

Wazne:

```text
/turtle1/cmd_vel -> geometry_msgs/msg/Twist
```

Struktura `Twist`:

```text
Vector3 linear
  float64 x
  float64 y
  float64 z
Vector3 angular
  float64 x
  float64 y
  float64 z
```

Szybki test predkosci:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}"
```

Rysowanie domyslnej litery P:

```bash
ros2 run pose_subscriber auto_p
```

## Launch

Plik:

```text
pose_subscriber/launch/auto_p_launch.py
```

W `setup.py` musi byc instalacja launchy:

```python
(os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
```

Uruchomienie:

```bash
ros2 launch pose_subscriber auto_p_launch.py
```

## Etap 3 - parametr `letter`

Litera P:

```bash
ros2 run pose_subscriber auto_p --ros-args -p letter:=P
```

Litera K:

```bash
ros2 run pose_subscriber auto_p --ros-args -p letter:=K
```

Opis parametru:

```bash
ros2 param describe /my_turtle_node letter
```

## Etap 4 - rqt

Predkosc katowa zolwia:

```bash
ros2 run rqt_plot rqt_plot /turtle1/pose/angular_velocity
```

Graf systemu:

```bash
ros2 run rqt_graph rqt_graph
```

## Sekwencja demo

Terminal 1:

```bash
ros2 launch pose_subscriber auto_p_launch.py
```

Terminal 2:

```bash
ros2 run rqt_graph rqt_graph
```

Terminal 3:

```bash
ros2 run rqt_plot rqt_plot /turtle1/pose/angular_velocity
```

Test K osobno:

```bash
ros2 run turtlesim turtlesim_node
```

```bash
ros2 run pose_subscriber auto_p --ros-args -p letter:=K
```
