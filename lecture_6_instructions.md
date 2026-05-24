<h1 align="center">Projekt szósty :robot:</h1>
<h3 align="center">Programowanie w ROS, semestr 26L</h3>


## Treść zadania

Celem projektu jest rozszerzenie sterowania manipulatorem o kinematykę różniczkową oraz ruch typu _point-to-point_ do punktu zadanego przez akcję ROS 2 lub wskazanego w _RViz_ narzędziem **Publish Point**.

W projekcie należy wykorzystać manipulator z poprzednich zajęć oraz pakiet `my_urdf_pkg`.

W katalogu `lab6` repozytorium z materiałami znajduje się plik:

```text
trajectory_generator.py
```

Plik należy skopiować do tworzonego pakietu `p2p_control`.


### :arrow_right: Etap 1

1. W istniejącym pakiecie, np. `gripper_ctrl`, utwórz nowy węzeł **DiffKin**.
2. Węzeł ma subskrybować temat:

```text
/joint_states
```

3. Na podstawie aktualnych pozycji złącz wyznacz analitycznie Jakobian manipulatora.
4. Korzystając z zależności:

```math
\dot{x} = J(q)\dot{q}
```

oblicz prędkość końcówki manipulatora.
5. Wynik opublikuj na temacie:

```text
/ee_velocity
```

Typ wiadomości:

```text
geometry_msgs/msg/TwistStamped
```

6. Wiadomość powinna zawierać co najmniej:
* `header.stamp`,
* `header.frame_id`,
* `twist.linear`,
* `twist.angular`.

7. Dodaj executable do `setup.py`, np.:

```python
'diff_kinematics = gripper_ctrl.diff_kin:main'
```

8. Przetestuj działanie węzła:

```bash
colcon build --packages-select gripper_ctrl
ros2 run gripper_ctrl diff_kinematics
ros2 topic echo /ee_velocity
```

9. Poruszaj manipulatorem z poziomu `joint_state_publisher_gui` i obserwuj zmiany prędkości końcówki.

Opcjonalnie można użyć:

```bash
ros2 run rqt_plot rqt_plot /ee_velocity/twist/linear/x
```


### :arrow_right: Etap 2

1. W pakiecie `my_urdf_pkg` utwórz plik akcji:

```text
action/MoveP2P.action
```

2. Akcja powinna mieć strukturę:

```text
geometry_msgs/Point target
float64 vmax
float64 amax
---
bool success
string message
---
float64 percent_complete
float64[] q_current
geometry_msgs/Point tcp_current
```

3. W `CMakeLists.txt` dodaj generowanie akcji:

```cmake
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GripperControl.srv"
  "action/DrawShape.action"
  "action/MoveP2P.action"
  DEPENDENCIES geometry_msgs
)
```

4. W `package.xml` upewnij się, że znajdują się potrzebne zależności:

```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<depend>geometry_msgs</depend>
<depend>action_msgs</depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

5. Zbuduj pakiet i sprawdź strukturę akcji:

```bash
colcon build --packages-select my_urdf_pkg
ros2 interface show my_urdf_pkg/action/MoveP2P
```


### :arrow_right: Etap 3

1. Utwórz nowy pakiet Python:

```bash
ros2 pkg create --build-type ament_python p2p_control --dependencies rclpy sensor_msgs geometry_msgs my_urdf_pkg numpy
```

2. Skopiuj plik:

```text
trajectory_generator.py
```

do katalogu:

```text
p2p_control/p2p_control/trajectory_generator.py
```

3. W pakiecie `p2p_control` utwórz plik:

```text
p2p_control/kinematics.py
```

4. W pliku należy zaimplementować:
* kinematykę prostą,
* kinematykę odwrotną,
* wybór rozwiązania najbliższego aktualnej konfiguracji złącz.

5. Dla punktów spoza przestrzeni roboczej należy zgłosić błąd, np. przez `ValueError`.


### :arrow_right: Etap 4

1. Utwórz serwer akcji:

```text
p2p_control/p2p_server.py
```

2. Serwer ma obsługiwać akcję:

```text
/move_p2p
```

typu:

```text
my_urdf_pkg/action/MoveP2P
```

3. Serwer ma subskrybować aktualny stan złącz z tematu:

```text
/joint_states
```

4. Kolejne zadane pozycje złącz publikuj na:

```text
/joint_states
```

Typ wiadomości:

```text
sensor_msgs/msg/JointState
```

5. Serwer powinien odrzucać nieprawidłowe zapytania:
* `vmax <= 0`,
* `amax <= 0`,
* brak aktualnej konfiguracji startowej,
* punkt poza przestrzenią roboczą.

6. W trakcie ruchu publikuj feedback:
* procent wykonania ruchu,
* aktualne pozycje złącz,
* aktualne położenie TCP.

7. Dodaj executable w `setup.py`:

```python
'p2p_server = p2p_control.p2p_server:main'
```

8. Przetestuj uruchomienie serwera:

```bash
colcon build --packages-select my_urdf_pkg p2p_control
ros2 run p2p_control p2p_server
```

9. Wyślij przykładowy cel:

```bash
ros2 action send_goal /move_p2p my_urdf_pkg/action/MoveP2P "{target: {x: 0.2, y: -0.6, z: 1.2}, vmax: 1.0, amax: 2.0}" --feedback
```


### :arrow_right: Etap 5

1. Rozszerz serwer P2P o obsługę punktu klikniętego w _RViz_.
2. Serwer ma subskrybować temat:

```text
/clicked_point
```

Typ wiadomości:

```text
geometry_msgs/msg/PointStamped
```

3. Po odebraniu punktu robot powinien rozpocząć ruch z aktualnej konfiguracji do wskazanego punktu.
4. Do ustawienia prędkości i przyspieszenia dla punktu klikniętego w _RViz_ użyj parametrów ROS 2, np.:

```text
default_vmax
default_amax
```

5. Przykład uruchomienia:

```bash
ros2 run p2p_control p2p_server --ros-args -p default_vmax:=1.0 -p default_amax:=2.0
```

6. W _RViz_ wybierz:

```text
Tool: Publish Point
Topic: /clicked_point
Fixed Frame: Base
```

7. Przetestuj kliknięcie kilku punktów z przestrzeni roboczej manipulatora.
8. Punkt spoza przestrzeni roboczej powinien zostać odrzucony, a w terminalu powinien pojawić się komunikat błędu.


## Komendy testowe

Uruchomienie manipulatora:

```bash
ros2 launch my_urdf_pkg display.launch.py
```

Uruchomienie serwera:

```bash
ros2 run p2p_control p2p_server
```

Publikacja konfiguracji początkowej, jeżeli `joint_state_publisher_gui` nie publikuje:

```bash
ros2 topic pub --once /joint_states sensor_msgs/msg/JointState "{name: ['Joint_1', 'Joint_2', 'Joint_3', 'Joint_5'], position: [0.0, -1.128, -1.279, 0.0], velocity: [0.0, 0.0, 0.0, 0.0]}"
```

Test bez _RViz_:

```bash
ros2 topic pub --once /clicked_point geometry_msgs/msg/PointStamped "{header: {frame_id: 'Base'}, point: {x: 0.2, y: -0.6, z: 1.2}}"
```

Wysłanie celu przez akcję:

```bash
ros2 action send_goal /move_p2p my_urdf_pkg/action/MoveP2P "{target: {x: 0.2, y: -0.6, z: 1.2}, vmax: 1.0, amax: 2.0}" --feedback
```

Podejrzenie tematów akcji:

```bash
ros2 topic list --include-hidden-topics
ros2 topic echo /move_p2p/_action/status
ros2 topic echo /move_p2p/_action/feedback
```


## Oddanie projektu

Należy zaprezentować Prowadzącemu:

1. Działanie węzła `DiffKin` i publikację `/ee_velocity`.
2. Poprawnie wygenerowaną akcję `MoveP2P`.
3. Pakiet `p2p_control` z działającym serwerem akcji.
4. Ruch manipulatora do punktu zadanego przez `ros2 action send_goal`.
5. Ruch manipulatora do punktu wskazanego w _RViz_ narzędziem **Publish Point**.
6. Odrzucanie błędnych celów, np. punktów spoza przestrzeni roboczej.


#### Zalecenia:

- Serwer P2P powinien znać aktualną konfigurację startową manipulatora przed przyjęciem celu.
- Jeżeli serwer odrzuca cel komunikatem o braku pozycji startowej, sprawdź temat `/joint_states`.
- W przypadku błędu `ImportError: cannot import name 'MoveP2P'`, przebuduj pakiet `my_urdf_pkg` i sprawdź wpis w `CMakeLists.txt`.
- W _RViz_ można dodać wizualizację klikniętych punktów przez `Add -> By topic -> /clicked_point`.