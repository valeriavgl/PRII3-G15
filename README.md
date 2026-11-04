# PRII3-G15
Proyecto RII 3: Robots Inteligentes

**Integrantes:** 
1. [Quijia Anaguano, Marley]
2. [Milla Villavicencio, Alexa] 
3. [Garcia Ledezma, Valeria] 

---

## Descripción
El proyecto consiste en la creación de un paquete en ROS 2 diseñado para que un robot móvil dibuje automáticamente el número "15" en el suelo. 

**Evolución del Proyecto:**
* **Sprint 1 (2D):** Desarrollo de la cinemática inicial en el simulador ideal `turtlesim`.
* **Sprint 2 (3D y Físico):** Migración del controlador al simulador Gazebo (modelo TurtleBot3 Waffle) y despliegue en hardware real (JetBot). Se ha integrado un sistema de seguridad (Collision Avoidance) mediante el escáner LiDAR y se ha adaptado la frecuencia de publicación a 10 Hz para garantizar la estabilidad del bus físico del robot.

---

## Requisitos Previos
Para ejecutar este proyecto necesitas tener instalado:
* **Sistema Operativo:** Ubuntu 22.04 LTS
* **ROS 2:** Distribución Humble Hawksbill
* **Paquetes de ROS:** `ros-humble-turtlesim`
* **Herramientas:** `git`, `colcon`, `tree`
- **Paquetes de ROS adicionales (Sprint 2):** 
  - `ros-humble-gazebo-ros-pkgs`
  - `ros-humble-turtlebot3*` (Paquetes de simulación y descripción del TurtleBot3)
- **Exportar modelo:** Antes de lanzar, es necesario tener exportado el modelo del robot en la terminal: `export TURTLEBOT3_MODEL=waffle`

---

## Estructura del Workspace

```text
PRII3-G15/
│───README.md
│   
└───src
    ├───g15_prii3_move_jetbot
    │   ├───g15_prii3_move_jetbot
    │   │   ├─── collision_avoidance.py
    │   │   ├─── draw_number_node.py
    │   │   ├─── __init__.py
    │   │   ├─── number_five.py
    │   │   └─── number_one.py
    │   ├───launch
    │   │   └─── move_jetbot.launch.py
    │   ├───package.xml
    │   ├───resource
    │   │   └─── g15_prii3_move_jetbot
    │   ├───rviz
    │   │   ├─── dibujo.rviz
    │   │   ├─── lidar_jetbot.rviz
    │   │   └─── lidar_simulacion.rviz
    │   ├───setup.cfg
    │   ├───setup.py
    │   └───test
    │       ├─── test_copyright.py
    │       ├─── test_flake8.py
    │       └─── test_pep257.py
    │
    ├───g15_prii3_move_turtlebot
    │   ├───g15_prii3_move_turtlebot
    │   │   ├─── collision_avoidance.py
    │   │   ├─── draw_number.py
    │   │   ├─── __init__.py
    │   │   ├─── number_five.py
    │   │   └─── number_one.py
    │   ├───launch
    │   │   └─── launch.py
    │   ├───models
    │   │   └─── cubo.sdf
    │   ├───package.xml
    │   ├───resource
    │   │   └─── g15_prii3_move_turtlebot
    │   ├───rviz
    │   │   ├─── dibujo.rviz
    │   │   ├─── lidar_jetbot.rviz
    │   │   └─── lidar_simulacion.rviz
    │   ├───setup.cfg
    │   ├───setup.py
    │   └───test
    │       ├─── test_copyright.py
    │       ├─── test_flake8.py
    │       └─── test_pep257.py
    │
    └───g15_prii3_turtlesim
        ├───g15_prii3_turtlesim
        │   ├─── comandos.txt
        │   ├─── __init__.py
        │   ├─── number_five.py
        │   ├─── number_one.py
        │   └─── writer_node.py
        ├───launch
        │   └─── launch.py
        ├───package.xml
        ├───resource
        │   └─── g15_prii3_turtlesim
        ├───setup.cfg
        ├───setup.py
        └───test
            ├─── test_copyright.py
            ├─── test_flake8.py
            └─── test_pep257.py
```
---

## Estructura de Desarrollo 
El proyecto ha sido dividido de manera modular para evitar conflictos de integración en Git:
- `writer_node.py` (Sprint 1) y `draw_number.py` (Sprint 2): Administran la lógica principal de ROS 2 y publican los comandos de velocidad en `cmd_vel`.
- `number_one.py` y `number_five.py`: Contienen la lógica matemática aislada (cinemática) para los trazos de cada número.
- `collision_avoidance.py`: Nodo de seguridad basado en el procesamiento de datos del LiDAR.

## Arquitectura y Novedades (Sprint 2)
Para el paso a hardware real y simulación 3D, el proyecto incorpora las siguientes mejoras:
1. **Evitación de Colisiones (LiDAR):** Un nodo independiente (`collision_avoidance`) procesa los datos del tópico `/scan`. Si detecta un obstáculo a menos de 0.5 metros en un cono frontal de 60º, pausa la rutina a través de un servicio personalizado y la reanuda al despejarse.
2. **Estabilidad Hardware (10 Hz):** La frecuencia de publicación del `cmd_vel` se ha reducido a 10 Hz para evitar la saturación de red y los tirones mecánicos en los motores del robot real.
3. **Graceful Shutdown:** Se ha implementado un bloque de apagado seguro (`try-except-finally`) para garantizar que el nodo destruye todas sus conexiones y detiene los motores de forma limpia al recibir una interrupción manual (Ctrl+C).

## Guía de Instalación y Ejecución

Sigue estos pasos en orden para descargar, compilar y ejecutar el proyecto.

### 1. Descargar el Workspace 
El repositorio de Git ya cuenta con la estructura necesaria de Workspace. Para descargarlo, abre una terminal (`Ctrl` + `Alt` + `T`) y ejecuta:

```bash
# Clonar el repositorio completo
git clone https://github.com/valeriavgl/PRII3-G15.git PRII3-G15

# Entrar a la carpeta del proyecto
cd PRII3-G15
```

### 2. Compilar el Paquete
Una vez dentro de la carpeta `PRII3-G15`, utilizamos `colcon` para compilar el código fuente. Esto generará automáticamente las carpetas `build`, `install` y `log`.

```bash
# Ejecutar la compilación desde la raíz del workspace
colcon build
```

### 3. Cargar el Entorno 
Para que ROS 2 pueda encontrar los nodos y el archivo launch, es necesario cargar las variables de entorno de la instalación principal y de nuestro workspace recién compilado.

```bash
# Cargar la configuración principal de ROS 2
source /opt/ros/humble/setup.bash

# Cargar la configuración de nuestro workspace local
source install/setup.bash
```
*(Nota: El comando de source local debe ejecutarse cada vez que se abra una terminal nueva para probar el código).*

### 4. Ejecución en Simulación 2D (Turtlesim - Sprint 1)
Luego de estos comandos, se ha preparado un archivo `launch` que levanta simultáneamente el simulador (`turtlesim_node`) y un nodo principal de dibujo (`writer_node`). En la misma terminal donde se realizó el paso anterior, ejecuta:

```bash
ros2 launch g15_prii3_turtlesim launch.py
```

**Resultado esperado:**
1. Se abrirá la ventana azul del simulador *Turtlesim*.
2. La terminal mostrará los *logs* (mensajes informativos) indicando el progreso.
3. La tortuga se moverá trazando el número "1" y, a continuación, el número "5".

**Pausa, reanudación y reinicio:**
- Es posible pausar, reanudar y reiniciar la simulación ejecutando los siguientes comandos en una nueva terminal:

```bash
# Para pausar la simulación
ros2 service call /control_dibujo std_srvs/srv/SetBool "{data: false}"

# Para reanudar la simulación
ros2 service call /control_dibujo std_srvs/srv/SetBool "{data: true}"

# Para reiniciar la simulación
ros2 service call /reiniciar_dibujo std_srvs/srv/Trigger {}

```
### 5. Ejecución en Simulación 3D (Gazebo y RViz - Sprint 2)
En este Sprint 2, hemos dado el salto del entorno 2D a la simulación física en 3D. Además de Gazebo, utilizamos la herramienta **RViz** para visualizar en tiempo real los datos del sensor LiDAR y monitorizar el sistema de evasión de colisiones.

Para ejecutar la simulación completa, abre dos terminales nuevas (recuerda ejecutar el comando `source install/setup.bash` en ambas):

**Terminal 1: Iniciar y Configurar RViz**
Carga la interfaz gráfica ejecutando:
```bash
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true 
```

**Configuración inicial (solo la primera vez):**
1. En el panel izquierdo, establece el **Fixed Frame** en `odom`.
2. Haz clic en el botón **Add** (abajo a la izquierda) -> selecciona **By display type** -> **Odometry**. En su apartado **Topic**, escribe `/odom`.
3. Para que no se borre el rastro del dibujo a medida que avanza, cambia el valor de **Keep** a `10000`.
4. Desmarca la casilla **Covariance** (para que las marcas de error no tapen toda la pantalla).
5. En los ajustes de visualización (Shape), pon **Head Length** en `0.05` y **Head Radius** en `0.03`.
6. Para no tener que repetir este proceso, guarda la configuración en el menú superior yendo a **File → Save Config As...** (puedes guardarlo como `dibujo.rviz`).

**Terminal 2: Lanzar Entorno Virtual y Controladores**
Gracias al nuevo archivo de lanzamiento integrado, este comando despliega simultáneamente el simulador Gazebo, el nodo de dibujo y el sistema de seguridad anticolisiones:
```bash
# Exportar el modelo del robot (Waffle)
export TURTLEBOT3_MODEL=waffle

# Lanzar simulación y nodos de control
ros2 launch g15_prii3_move_turtlebot launch.py
```
*(Se abrirá Gazebo y el robot comenzará a trazar los números).*

**Terminal 3: Prueba del Sistema Anticolisiones (LiDAR)**
Para verificar el funcionamiento del nodo `collision_avoidance`, en lugar de hacerlo gráficamente, podemos inyectar un obstáculo directamente en la trayectoria usando la terminal:

1. **Aparecer el obstáculo (El robot debe detenerse):**
```bash
# Asegúrate de estar ejecutando esto desde la raíz del workspace (PRII3-G15)
ros2 run gazebo_ros spawn_entity.py -entity cubo -file src/g15_prii3_move_turtlebot/models/cubo.sdf -x -1.0 -y -0.8 -z 0.0
```
*En RViz observarás cómo el láser detecta la silueta del cubo. Al estar a menos de 0.5m en el cono frontal, el robot se detendrá de forma segura.*

2. **Eliminar el obstáculo (El robot debe reanudar):**
```bash
ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'cubo'}"
```
*El cubo se eliminará del entorno de Gazebo y el robot reanudará su trazo automáticamente.*

### 6. Cierre y Detención
Para detener la ejecución de manera segura:
1. Ve a la terminal donde se están ejecutando los nodos (Terminal 2 en el caso 3D).
2. Presiona la combinación de teclas: **`Ctrl + C`**
3. El bloque *Graceful Shutdown* garantizará que el nodo finalice y los motores se detengan completamente de forma limpia. Repite el proceso para cerrar RViz.

---

