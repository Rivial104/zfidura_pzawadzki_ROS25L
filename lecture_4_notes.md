# Lecture 4 - projekt 3

Pakiety:

```text
my_urdf_pkg  - URDF chwytaka, serwis GripperControl
gripper_ctrl - serwer/klient chwytaka, odwrotna kinematyka
```

## Build

```bash
colcon build --packages-select my_urdf_pkg gripper_ctrl
```

## Etap 1 - URDF z chwytakiem

Plik:

```text
my_urdf_pkg/urdf/manipulator_model_with_gripper.urdf
```

Uruchom RViz:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Sprawdzenie jointow:

```bash
ros2 topic echo /joint_states --once
```

Wazne:

```text
Joint_5 - szczeka chwytaka
Joint_6 - mimic Joint_5
```

## Etap 2 - serwis `GripperControl`

Plik:

```text
my_urdf_pkg/srv/GripperControl.srv
```

Struktura:

```bash
ros2 interface show my_urdf_pkg/srv/GripperControl
```

```text
string state
---
bool success
string message
```

## Etap 3 - sterowanie chwytakiem

Terminal 1 - RViz:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Po starcie zamknij okno `joint_state_publisher_gui`, zeby nie nadpisywal `/joint_states`.

Terminal 2 - serwer:

```bash
ros2 run gripper_ctrl service
```

Terminal 3 - klient:

```bash
ros2 run gripper_ctrl client open
```

Wywolania z terminala:

```bash
ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: open}"
ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: close}"
ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: abcd}"
```

Oczekiwane odpowiedzi:

```text
open  -> success=True,  message="Gripper opened"
close -> success=True,  message="Gripper closed"
abcd  -> success=False, message="Unknown command"
```

Sprawdzenie serwisu:

```bash
ros2 service list
ros2 service type /control_gripper
```

## Etap 4 - odwrotna kinematyka

Terminal 1 - RViz:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Po starcie zamknij `joint_state_publisher_gui`.

Terminal 2 - IK:

```bash
ros2 run gripper_ctrl inv_kin
```

W RViz:

```text
Tool: Publish Point
Topic: /clicked_point
Add -> By topic -> /clicked_point PointStamped
```

Ustawienia grid:

```text
Plane Cell Count: 5
Normal Cell Count: 5
Offset: 0; 0; 2
Cell Size: 0.3
```

Sprawdzenie kliknietego punktu:

```bash
ros2 topic echo /clicked_point --once
```

Sprawdzenie publikowanych jointow:

```bash
ros2 topic echo /joint_states --once
```

## Sekwencja demo

Terminal 1:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Terminal 2:

```bash
ros2 run gripper_ctrl service
```

Terminal 3:

```bash
ros2 run gripper_ctrl client open
ros2 service call /control_gripper my_urdf_pkg/srv/GripperControl "{state: close}"
```

Terminal 4:

```bash
ros2 run gripper_ctrl inv_kin
```

