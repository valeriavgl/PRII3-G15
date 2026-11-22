#!/usr/bin/env python3
import math
import re
import cv2
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class AutonomousNavigation(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')

      
        # ZONA DE CONFIGURACION
        self.declare_parameter('topic_camara', '/camera/image_raw')
        self.declare_parameter('topic_aruco', '/aruco_detections')
        self.declare_parameter('usar_topico_texto', False)

        # Pose intermedia en la puerta del laboratorio 
        self.declare_parameter('puerta_x', -2.0)
        self.declare_parameter('puerta_y', -4.2)
        self.declare_parameter('puerta_yaw', 1.57)

        #  poses finales prueba  distintas según los 3 ArUco 
        self.declare_parameter('id_aruco_1', 5)
        self.declare_parameter('dest1_x', 1.2)
        self.declare_parameter('dest1_y', -3.3)
        self.declare_parameter('dest1_yaw', 0.0)

        self.declare_parameter('id_aruco_2', 6)
        self.declare_parameter('dest2_x', -2.8)
        self.declare_parameter('dest2_y', -2.4)
        self.declare_parameter('dest2_yaw', 1.57)

        self.declare_parameter('id_aruco_3', 17)
        self.declare_parameter('dest3_x', -2.3)
        self.declare_parameter('dest3_y', -2.2)
        self.declare_parameter('dest3_yaw', -1.57)
       

        self.navigator = BasicNavigator()
        self.bridge = CvBridge()

        # Diccionario 
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        if hasattr(cv2.aruco, 'ArucoDetector'):
            self._aruco_detector = cv2.aruco.ArucoDetector(
                self.aruco_dict, cv2.aruco.DetectorParameters()
            )
            self._detectar_aruco = lambda gray: self._aruco_detector.detectMarkers(gray)
        else:
            self._aruco_params = cv2.aruco.DetectorParameters_create()
            self._detectar_aruco = lambda gray: cv2.aruco.detectMarkers(
                gray, self.aruco_dict, parameters=self._aruco_params
            )

        topic_camara = self.get_parameter('topic_camara').value
        topic_aruco = self.get_parameter('topic_aruco').value

        self.sub_camara = self.create_subscription(
            Image, topic_camara, self.callback_camara, 10
        )
        self.sub_texto = self.create_subscription(
            String, topic_aruco, self.callback_texto, 10
        )

        # Estados
        self.estado = 'IR_PUERTA'
        self.meta_enviada = False
        self.nav2_listo = False
        self.aruco_leido = None

        self.timer = self.create_timer(0.5, self.callback_maquina_estados)
        self.get_logger().info('Nodo autonomous_navigation inicializado correctamente.')

    def crear_pose_stamped(self, x: float, y: float, yaw: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.z = math.sin(float(yaw) / 2.0)
        pose.pose.orientation.w = math.cos(float(yaw) / 2.0)
        return pose

    def obtener_destinos(self) -> dict:
        return {
            int(self.get_parameter('id_aruco_1').value): (
                float(self.get_parameter('dest1_x').value),
                float(self.get_parameter('dest1_y').value),
                float(self.get_parameter('dest1_yaw').value),
            ),
            int(self.get_parameter('id_aruco_2').value): (
                float(self.get_parameter('dest2_x').value),
                float(self.get_parameter('dest2_y').value),
                float(self.get_parameter('dest2_yaw').value),
            ),
            int(self.get_parameter('id_aruco_3').value): (
                float(self.get_parameter('dest3_x').value),
                float(self.get_parameter('dest3_y').value),
                float(self.get_parameter('dest3_yaw').value),
            ),
        }

    def callback_camara(self, msg: Image):
        if self.estado != 'LEER_ARUCO' or self.get_parameter('usar_topico_texto').value:
            return
        if self.aruco_leido is not None:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, ids, _ = self._detectar_aruco(gray)

            if ids is not None:
                destinos = self.obtener_destinos()
                for marker_id in ids.flatten():
                    marker_id = int(marker_id)
                    if marker_id in destinos:
                        self.aruco_leido = marker_id
                        self.get_logger().info(f'ArUco detectado por camara: ID = {marker_id}')
                        break
        except Exception as e:
            self.get_logger().error(f'Error procesando imagen ArUco: {e}')

    def callback_texto(self, msg: String):
        if self.estado != 'LEER_ARUCO' or not self.get_parameter('usar_topico_texto').value:
            return
        if self.aruco_leido is not None:
            return

        numeros = [int(n) for n in re.findall(r'\d+', msg.data)]
        destinos = self.obtener_destinos()
        for marker_id in destinos.keys():
            if marker_id in numeros:
                self.aruco_leido = marker_id
                self.get_logger().info(f'ArUco recibido por topico: ID = {marker_id}')
                break

    def callback_maquina_estados(self):
        #  ESTADO 1
        if self.estado == 'IR_PUERTA':
            if not self.nav2_listo:
                self.get_logger().info('Esperando a que Nav2 este activo...')
                self.navigator.waitUntilNav2Active()
                self.nav2_listo = True

            if not self.meta_enviada:
                px = float(self.get_parameter('puerta_x').value)
                py = float(self.get_parameter('puerta_y').value)
                pyaw = float(self.get_parameter('puerta_yaw').value)
                self.get_logger().info(f'Yendo a la puerta: ({px}, {py}, {pyaw})')
                self.navigator.goToPose(self.crear_pose_stamped(px, py, pyaw))
                self.meta_enviada = True
                return

            if self.navigator.isTaskComplete():
                if self.navigator.getResult() == TaskResult.SUCCEEDED:
                    self.get_logger().info('Llegada a la puerta. Buscando ArUco...')
                    self.estado = 'LEER_ARUCO'
                    self.meta_enviada = False
                else:
                    self.get_logger().error('Fallo al llegar a la puerta.')
                    self.estado = 'FIN'
                    self.timer.cancel()

        # ESTADO 2
        elif self.estado == 'LEER_ARUCO':
            if self.aruco_leido is not None:
                self.estado = 'IR_DESTINO'

        #  ESTADO 3
        elif self.estado == 'IR_DESTINO':
            if not self.meta_enviada:
                destinos = self.obtener_destinos()
                dx, dy, dyaw = destinos[self.aruco_leido]
                self.get_logger().info(
                    f'ArUco ID  Navegando a destino final ({dx}, {dy}, {dyaw})'
                )
                self.navigator.goToPose(self.crear_pose_stamped(dx, dy, dyaw))
                self.meta_enviada = True
                return

            if self.navigator.isTaskComplete():
                if self.navigator.getResult() == TaskResult.SUCCEEDED:
                    self.get_logger().info('Navegacion autonoma completada con exito!')
                else:
                    self.get_logger().warn('No se pudo alcanzar el destino final.')
                self.estado = 'FIN'
                self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    nodo = AutonomousNavigation()
    executor = SingleThreadedExecutor()
    executor.add_node(nodo)
    try:
        executor.spin()
    except KeyboardInterrupt:
        nodo.navigator.cancelTask()
    finally:
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
