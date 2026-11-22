# Parámetros del Nodo `aruco_detector`

Para modificar cualquier parámetro desde la terminal sin tocar el código, añade `--ros-args` seguido de `-p nombre:=valor` al ejecutar el nodo. Puedes cambiar un solo parámetro o combinar varios en la misma línea.

## Tabla de parámetros disponibles

| Parámetro | Valor por defecto | Descripción | Ejemplo para cambiarlo | 
| ----- | ----- | ----- | ----- | 
| **`topic_camara`** | `/camera/image_raw` | Tópico de entrada con las imágenes de la cámara | `-p topic_camara:=/image_raw` | 
| **`topic_salida`** | `/arucos` | Tópico propio donde se publican los IDs y coordenadas | `-p topic_salida:=/mis_arucos` | 
| **`periodo`** | `0.5` | Segundos entre cada publicación del temporizador | `-p periodo:=1.0` | 
| **`calib_path`** | `../camera/calibration/calibracion_camara.yml` | Ruta al archivo `.yml` de calibración de la cámara | `-p calib_path:=/home/valeria/calib.yml` | 
| **`marker_size`** | `0.1` | Tamaño real del lado del ArUco en metros | `-p marker_size:=0.05` | 
| **`use_sim_time`** | `false` | Usa el reloj de Gazebo (parámetro propio de ROS 2) | `-p use_sim_time:=true` | 

## Ejemplos de ejecución

### 1. En Gazebo (simulación)

Activa el tiempo de simulación para sincronizarse con Gazebo:

```bash
python3 aruco_detector.py --ros-args -p use_sim_time:=true
```

### 2. En el JetBot (robot físico)

Usando todos los valores por defecto:

```bash
python3 aruco_detector.py
```

### 3. Con la cámara de la computadora (webcam)

Para usar la webcam del portátil o una cámara USB sin modificar el código, primero debes publicar la cámara en ROS 2 (por ejemplo, con `v4l2_camera`) y luego apuntar tu nodo a ese tópico.

**Paso 1 (Terminal 1):** Publica la webcam en ROS 2 (normalmente publica en `/image_raw`):

```bash
ros2 run v4l2_camera v4l2_camera_node
```

*(Si no lo tienes instalado, puedes instalarlo con `sudo apt install ros-$ROS_DISTRO-v4l2-camera`)*

**Paso 2 (Terminal 2):** Lanza tu nodo cambiando `topic_camara` al tópico de la webcam:

```bash
python3 aruco_detector.py --ros-args -p topic_camara:=/image_raw
```

*(Si usas `usb_cam` en lugar de `v4l2_camera`, comprueba el nombre exacto del tópico con `ros2 topic list` y pásalo en `-p topic_camara:=...`)*

### 4. Combinando varios parámetros a la vez

Por ejemplo, publicando cada 1 segundo, con marcadores de 5 cm y una ruta específica de calibración:

```bash
python3 aruco_detector.py --ros-args -p periodo:=1.0 -p marker_size:=0.05 -p calib_path:=/ruta/a/tu/calibracion.yml
```

### 5. Ejecutando desde el paquete compilado (`ros2 run`)

La sintaxis al final del comando es exactamente la misma:

```bash
ros2 run nombre_paquete aruco_detector --ros-args -p periodo:=1.0
```

## Comprobación en tiempo real

Abre una terminal adicional para verificar los IDs y coordenadas publicadas:

```bash
ros2 topic echo /arucos
```