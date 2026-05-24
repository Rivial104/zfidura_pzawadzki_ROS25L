# Lecture 6 - P2P control

Pakiety:

```text
my_urdf_pkg  - akcja MoveP2P
p2p_control  - serwer i klient ruchu point-to-point
```

## Build po zmianach w akcji

```bash
colcon build --packages-select my_urdf_pkg p2p_control
```

Sprawdzenie interfejsu:

```bash
ros2 interface show my_urdf_pkg/action/MoveP2P
ros2 pkg executables p2p_control
```

## Uruchomienie P2P

Terminal 1 - RViz/manipulator:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Terminal 2 - serwer akcji:

```bash
ros2 run p2p_control p2p_server
```

Serwer slucha:

```text
/joint_states   - aktualna pozycja startowa
/clicked_point  - cel z RViz Publish Point
/move_p2p       - akcja P2P
```

Terminal 3 - pozycja startowa, gdy nie uzywasz GUI:

```bash
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['Joint_1', 'Joint_2', 'Joint_3', 'Joint_5'], position: [0.0, -1.128, -1.279, 0.0], velocity: [0.0, 0.0, 0.0, 0.0]}"
```

## Sterowanie przez Publish Point

W RViz wybierz:

```text
Tool: Publish Point
Topic: /clicked_point
Fixed Frame: Base
```

Klikniecie punktu publikuje cel na `/clicked_point`, a `p2p_server` jedzie z obecnej pozycji manipulatora do tego punktu.

Parametry predkosci dla klikniecia:

```bash
ros2 run p2p_control p2p_server --ros-args -p default_vmax:=1.0 -p default_amax:=2.0
```

Test bez RViz:

```bash
ros2 topic pub --once /clicked_point geometry_msgs/msg/PointStamped "{header: {frame_id: 'Base'}, point: {x: 0.2, y: -0.6, z: 1.2}}"
```

## Goal przez klienta

```bash
ros2 run p2p_control p2p_client 0.2 -0.6 1.2 1.0 2.0
```

Ten klient wysyla:

```text
x=0.2, y=-0.6, z=1.2, vmax=1.0, amax=2.0
```

## Goal bez klienta

```bash
ros2 action send_goal /move_p2p my_urdf_pkg/action/MoveP2P "{target: {x: 0.2, y: -0.6, z: 1.2}, vmax: 1.0, amax: 2.0}" --feedback
```

## Debug

Lista akcji:

```bash
ros2 action list
ros2 action info /move_p2p
```

Status i feedback:

```bash
ros2 topic list --include-hidden-topics
ros2 topic echo /move_p2p/_action/status
ros2 topic echo /move_p2p/_action/feedback
```

Joint states:

```bash
ros2 topic echo /joint_states
```

## Naprawiony blad importu `MoveP2P`

Problem:

```text
ImportError: cannot import name 'MoveP2P' from 'my_urdf_pkg.action'
```

Przyczyna:

```text
MoveP2P.action uzywa geometry_msgs/Point, ale my_urdf_pkg nie generowal interfejsu z DEPENDENCIES geometry_msgs albo pakiet nie byl przebudowany.
```

Naprawa:

```bash
colcon build --packages-select my_urdf_pkg p2p_control
ros2 interface show my_urdf_pkg/action/MoveP2P
```
