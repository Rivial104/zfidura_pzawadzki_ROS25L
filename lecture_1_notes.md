# Lecture 1 - przygotowanie stanowiska, ROS 2 i Git

Data zajec: 24.02.2025

## 1. Sprawdzenie instalacji ROS 2

W kazdym nowym terminalu najpierw zaladuj srodowisko ROS 2:

```bash
```

Sprawdz, czy dostepne sa podstawowe narzedzia:

```bash
ros2 topic list
colcon --help
git --version
```

## 2. Minimalny test ROS 2 z turtlesim

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
ros2 topic echo /turtle1/pose
```

Najwazniejsze tematy z pierwszych zajec:

```text
/turtle1/pose     - aktualna pozycja zolwia
/turtle1/cmd_vel  - predkosc zadawana zolwiowi
```

Struktura pozycji:

```bash
ros2 interface show turtlesim/msg/Pose
```

Oczekiwany wynik:

```text
float32 x
float32 y
float32 theta

float32 linear_velocity
float32 angular_velocity
```
