# PRII3-G15
Proyecto RII 3: Robots Inteligentes

**Integrantes:** 
1. [Quijia Anaguano, Marley]
2. [Milla Villavicencio, Alexa] 
3. [Garcia Ledezma, Valeria] 

---

## Descripción
Este proyecto consiste en la creación de un paquete en ROS 2 diseñado con el fin de controlar la tortuga del simulador `turtlesim`.El propósito de la simulación es buscar que la tortuga dibuje automáticamente el número "15" en la pantalla.

El repositorio está estructurado para funcionar directamente como un Workspace de ROS 2, facilitando su descarga y compilación.

---

## Requisitos Previos
Para ejecutar este proyecto necesitas tener instalado:
* **Sistema Operativo:** Ubuntu 22.04 LTS
* **ROS 2:** Distribución Humble Hawksbill
* **Paquetes de ROS:** `ros-humble-turtlesim`
* **Herramientas:** `git`, `colcon`, `tree`

---

## Estructura del Workspace REVISAR CON TREE, Y ACTUALIZARLO (BORRAR EL LOG, INSTALL Y BUILD)

```text
PRII3-G15/
│───README.md
│   
└───src
    └───g15_prii3_turtlesim
        │   package.xml
        │   setup.cfg
        │   setup.py
        │   
        ├───g15_prii3_turtlesim
        │       number_five.py
        │       number_one.py
        │       test_number.py
        │       writer_node.py
        │       __init__.py
        │       
        ├───launch
        │       launch.py
        │       
        ├───resource
        │       g15_prii3_turtlesim
        │       
        └───test
                test_copyright.py
                test_flake8.py
                test_pep257.py
```
---

## Estructura de Desarrollo 
El proyecto ha sido dividido de manera modular para evitar conflictos de integración en Git:
* `writer_node.py`: Administra la lógica de ROS 2 y publica en `cmd_vel`.
* `number_1.py` y `number_5.py`: Contienen la lógica matemática aislada (cinemática) para los trazos de cada número.

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

### 4. Ejecución Automática (Launch)
Luego de estos comandos, se ha preparado un archivo `launch` que levanta simultáneamente el simulador (`turtlesim_node`) y un nodo principal de dibujo (`writer_node`). En la misma terminal donde se realizó el paso anterior, ejecuta:

```bash
ros2 launch g15_prii3_turtlesim draw_15.launch.py
```

**Resultado esperado:**
1. Se abrirá la ventana azul del simulador *Turtlesim*.
2. La terminal mostrará los *logs* (mensajes informativos) indicando el progreso.
3. La tortuga se moverá trazando el número "1" y, a continuación, el número "5".

**Pausa y reanudación:**
- Es posible pausar o reanudar la simulación ejecutando el siguiente comando en una nueva terminal:
    <""> 

### 5. Cierre y Detención
Para detener la ejecución de manera segura:
1. Ve a la terminal donde se está ejecutando el comando launch.
2. Presiona la combinación de teclas: **`Ctrl + C`**
3. Espera un par de segundos a que los nodos finalicen sus procesos y la ventana se cierre.

---

