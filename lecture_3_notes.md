# Lecture 3 - projekt 2

Pakiety:

```text
my_urdf_pkg - URDF, RViz, robot_state_publisher
for_kin     - kinematyka prosta, /fwd_kin, TF Base -> TCP
```

## Build

```bash
colcon build --packages-select my_urdf_pkg for_kin
```

## Etap 1 - URDF w RViz

Uruchom model:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Wersja bez chwytaka:

```bash
ros2 launch my_urdf_pkg display.launch.py model:=$(ros2 pkg prefix my_urdf_pkg)/share/my_urdf_pkg/urdf/manipulator_model.urdf
```

Sprawdzenie ramek:

```bash
ros2 topic list
ros2 topic echo /joint_states --once
ros2 run tf2_tools view_frames
```

Wazne:

```text
Joint_1, Joint_2, Joint_3 - zlacza obrotowe
tool_null                - koncowka manipulatora z URDF
Base                     - uklad bazowy
```

## Etap 2 - kinematyka prosta

Terminal 1:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Terminal 2:

```bash
ros2 run for_kin ForwardKin
```

Sprawdzenie wejscia:

```bash
ros2 topic echo /joint_states --once
```

Sprawdzenie wyjscia:

```bash
ros2 topic echo /fwd_kin --once
ros2 topic info /fwd_kin
```

Wazne:

```text
/joint_states -> sensor_msgs/msg/JointState
/fwd_kin      -> geometry_msgs/msg/PoseStamped
```

W RViz dodaj:

```text
Add -> By topic -> /fwd_kin
Shape: Axes
Fixed Frame: Base
```

## Etap 3 - TF `Base -> TCP`

Przy uruchomionym `ForwardKin`:

```bash
ros2 run tf2_ros tf2_echo Base TCP
```

Sprawdzenie drzewa TF:

```bash
ros2 run tf2_tools view_frames
```

Oczekiwany efekt:

```text
TCP pokrywa sie z tool_null
/fwd_kin pokazuje te sama pozycje co TCP
```

## Szybka publikacja testowa `/joint_states`

Gdy nie uzywasz GUI:

```bash
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{header: {frame_id: ''}, name: ['Joint_1', 'Joint_2', 'Joint_3'], position: [0.0, 0.0, 0.0]}"
```

Inny test:

```bash
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{header: {frame_id: ''}, name: ['Joint_1', 'Joint_2', 'Joint_3'], position: [0.5, -0.4, 0.3]}"
```

## Sekwencja demo

Terminal 1:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Terminal 2:

```bash
ros2 run for_kin ForwardKin
```

Terminal 3:

```bash
ros2 topic echo /fwd_kin
```

Terminal 4:

```bash
ros2 run tf2_ros tf2_echo Base TCP
```

