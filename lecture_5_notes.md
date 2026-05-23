# Lecture 5 - projekt 4

Pakiety:

```text
my_urdf_pkg   - akcja DrawShape
drawing_shape - serwer akcji, status, markery RViz
```

## Build

```bash
colcon build --packages-select my_urdf_pkg drawing_shape
```

## Etap 1 - akcja `DrawShape`

Plik:

```text
my_urdf_pkg/action/DrawShape.action
```

Struktura:

```bash
ros2 interface show my_urdf_pkg/action/DrawShape
```

```text
float64 time_of_motion
string shape_to_draw
float64 figure_param
---
bool success
string message
---
float64 percent_complete
```

## Etap 2 - serwer akcji

Terminal 1 - RViz:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Pozycja startowa:

```text
[0.00, -1.128, -1.279, 0.000]
```

Terminal 2 - serwer akcji:

```bash
ros2 run drawing_shape drawing_action_server_exe
```

Lista akcji:

```bash
ros2 action list
ros2 action info /draw_shape
```

Poprawny goal:

```bash
ros2 action send_goal /draw_shape my_urdf_pkg/action/DrawShape "{time_of_motion: 10.0, shape_to_draw: 'square', figure_param: 0.5}" --feedback
```

Bledny czas:

```bash
ros2 action send_goal /draw_shape my_urdf_pkg/action/DrawShape "{time_of_motion: -5.0, shape_to_draw: 'square', figure_param: 0.1}"
```

Bledny ksztalt/parametr:

```bash
ros2 action send_goal /draw_shape my_urdf_pkg/action/DrawShape "{time_of_motion: 10.0, shape_to_draw: 'triangle', figure_param: -1.2}"
```

## Status i feedback

Ukryte tematy akcji:

```bash
ros2 topic list --include-hidden-topics
```

Feedback:

```bash
ros2 topic echo /draw_shape/_action/feedback
```

Status:

```bash
ros2 topic echo /draw_shape/_action/status
```

Albo gotowy node statusu:

```bash
ros2 run drawing_shape robot_status
```

## Markery RViz

Temat markerow:

```text
/marker_example
```

W RViz:

```text
Add -> By topic -> /marker_example Marker
Fixed Frame: Base
```

Test samych markerow:

```bash
ros2 run drawing_shape rviz_marker_example
```

## Sekwencja demo

Terminal 1:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Terminal 2:

```bash
ros2 run drawing_shape drawing_action_server_exe
```

Terminal 3:

```bash
ros2 topic echo /draw_shape/_action/status
```

Terminal 4:

```bash
ros2 topic echo /draw_shape/_action/feedback
```

Terminal 5:

```bash
ros2 action send_goal /draw_shape my_urdf_pkg/action/DrawShape "{time_of_motion: 10.0, shape_to_draw: 'square', figure_param: 0.5}" --feedback
```