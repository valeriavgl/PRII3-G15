#!/usr/bin/env python3
import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# ==============================================================================
# ZONA DE CONFIGURACIÓN (EDITAR VALERIA / ALEXA / MARLEY PARA SINCRONIZAR)
# ==============================================================================
# 1. Tópicos (Cambiar si en el robot real o en el nodo de Alexa se llaman distinto)
TOPIC_CAMARA = '/camera/image_raw'       # Tópico de imagen (por si leemos directo de cámara)
TOPIC_ARUCO_ID = '/aruco_detections'     # Tópico de texto si el nodo de Alexa ya publica los IDs

# 2. Modo de lectura de ArUco:
# True  = Este nodo lee la cámara directamente con OpenCV (DICT_4X4_100)
# False = Este nodo escucha el tópico de texto que publica el nodo de Alexa
LEER_DESDE_CAMARA = True

# 3. Coordenadas en el mapa (x, y, yaw_en_radianes)
# Sacar estos valores mirando en RViz ("2D Pose Estimate" / "Publish Point") sobre el mapa F1L3
POSE_PUERTA = (2.5, 0.0, 0.0)            # Pose intermedia frente a la puerta del laboratorio

# Diccionario de 3 ArUcos distintos -> 3 poses finales distintas dentro del lab F1L3 (PBI 3.4)
DESTINOS_POR_ARUCO = {
    1: (4.5,  1.2,  1.57),   # Si lee ArUco ID 1 -> va al Punto A
    2: (5.0, -1.0,  0.00),   # Si lee ArUco ID 2 -> va al Punto B
    3: (3.8, -2.2, -1.57),   # Si lee ArUco ID 3 -> va al Punto C
}
# ==============================================================================


def crear_pose_stamped(navigator: BasicNavigator, x: float, y: float, yaw: float) -> PoseStamped:
    """Convierte (x, y, yaw) al mensaje PoseStamped con cuaternión que exige Nav2."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0

    # Conversión de ángulo yaw (radianes) a cuaternión (z, w)
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


class AutonomousNavigationNode(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')
        self.bridge = CvBridge()
        self.aruco_detectado = None
        self.escuchando_aruco = False

        # Configuración diccionario Eurobot 2027 exigido en PBI 3.4: DICT_4X4_100
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        # Suscriptor 1: Cámara directa (fallback autónomo)
        self.sub_camara = self.create_subscription(
            Image, TOPIC_CAMARA, self.callback_imagen, 10
        )

        # Suscriptor 2: Tópico de texto de Alexa (si ya publica el ID ahí)
        self.sub_aruco_txt = self.create_subscription(
            String, TOPIC_ARUCO_ID, self.callback_aruco_texto, 10
        )

        self.get_logger().info('Nodo autonomous_navigation inicializado correctamente.')

    def callback_imagen(self, msg: Image):
        """Procesa la imagen en la puerta para detectar el ID del ArUco."""
        if not self.escuchando_aruco or not LEER_DESDE_CAMARA:
            return
        if self.aruco_detectado is not None:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = self.detector.detectMarkers(gray)

            if ids is not None:
                for marker_id in ids.flatten():
                    marker_id = int(marker_id)
                    if marker_id in DESTINOS_POR_ARUCO:
                        self.aruco_detectado = marker_id
                        self.get_logger().info(f'¡ArUco válido detectado por cámara! ID = {marker_id}')
                        break
        except Exception as e:
            self.get_logger().error(f'Error procesando imagen ArUco: {e}')

    def callback_aruco_texto(self, msg: String):
        """Lee el ID si el nodo de Alexa ya lo publica en formato texto (PBI 3.1)."""
        if not self.escuchando_aruco or LEER_DESDE_CAMARA:
            return
        if self.aruco_detectado is not None:
            return

        # Busca si alguno de los IDs configurados (1, 2 o 3) aparece en el mensaje de texto
        for marker_id in DESTINOS_POR_ARUCO.keys():
            if f'ID:{marker_id}' in msg.data or f'id={marker_id}' in msg.data or msg.data.strip() == str(marker_id):
                self.aruco_detectado = marker_id
                self.get_logger().info(f'¡ArUco válido recibido por tópico! ID = {marker_id}')
                break


def main(args=None):
    rclpy.init(args=args)
    nodo = AutonomousNavigationNode()
    navigator = BasicNavigator()

    try:
        # Esperar a que Nav2 (de Valeria) esté activo y listo
        nodo.get_logger().info('Esperando a que Nav2 esté activo...')
        navigator.waitUntilNav2Active()

        # ------------------------------------------------------------------
        # ESTADO 1: NAVEGAR DESDE EL PASILLO HASTA LA PUERTA DEL LABORATORIO
        # ------------------------------------------------------------------
        nodo.get_logger().info(f'ESTADO 1: Yendo a la puerta del laboratorio {POSE_PUERTA}...')
        goal_puerta = crear_pose_stamped(navigator, *POSE_PUERTA)
        navigator.goToPose(goal_puerta)

        while not navigator.isTaskComplete():
            rclpy.spin_once(nodo, timeout_sec=0.1)

        if navigator.getResult() != TaskResult.SUCCEEDED:
            nodo.get_logger().error('No se pudo llegar a la puerta. Abortando secuencia.')
            return

        nodo.get_logger().info('¡Llegada a la puerta completada!')

        # ------------------------------------------------------------------
        # ESTADO 2: LEER CÓDIGO ARUCO EN LA PUERTA
        # ------------------------------------------------------------------
        nodo.get_logger().info('ESTADO 2: Buscando marcador ArUco (DICT_4X4_100)...')
        nodo.escuchando_aruco = True

        tiempo_inicio = time.time()
        timeout_segundos = 20.0  # Tiempo máximo esperando ver el ArUco

        while nodo.aruco_detectado is None and (time.time() - tiempo_inicio) < timeout_segundos:
            rclpy.spin_once(nodo, timeout_sec=0.1)

        nodo.escuchando_aruco = False

        if nodo.aruco_detectado is None:
            nodo.get_logger().warn('Tiempo agotado sin detectar ArUco válido (IDs 1, 2 o 3).')
            return

        # ------------------------------------------------------------------
        # ESTADO 3: IR AL DESTINO FINAL SEGÚN EL ID DEL ARUCO LEÍDO
        # ------------------------------------------------------------------
        id_leido = nodo.aruco_detectado
        pose_final = DESTINOS_POR_ARUCO[id_leido]
        nodo.get_logger().info(f'ESTADO 3: ArUco ID {id_leido} -> Navegando a pose final {pose_final}...')

        goal_final = crear_pose_stamped(navigator, *pose_final)
        navigator.goToPose(goal_final)

        while not navigator.isTaskComplete():
            rclpy.spin_once(nodo, timeout_sec=0.1)

        if navigator.getResult() == TaskResult.SUCCEEDED:
            nodo.get_logger().info(f'¡ÉXITO! Robot en destino final del ArUco {id_leido}.')
        else:
            nodo.get_logger().warn('La navegación al destino final no terminó con éxito.')

    except KeyboardInterrupt:
        nodo.get_logger().info('Interrupción manual (Ctrl+C). Deteniendo navegación...')
        navigator.cancelTask()
    finally:
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
