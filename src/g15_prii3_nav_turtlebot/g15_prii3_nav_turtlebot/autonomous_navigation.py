#!/usr/bin/env python3
import math
import re
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class AutonomousNavigation(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')

        # ZONA DE CONFIGURACION
        self.declare_parameter('topic_aruco', '/arucos')

        # Pose inicial en el mapa
        self.declare_parameter('initial_x', -2.06)
        self.declare_parameter('initial_y', -11.79)
        self.declare_parameter('initial_yaw', 0.0)

        # Pose intermedia en la puerta del laboratorio
        self.declare_parameter('puerta_x', 0.78)
        self.declare_parameter('puerta_y', -10.95)
        self.declare_parameter('puerta_yaw', 1.67)

        # Tres poses finales predefinidas segun el ID del ArUco
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
        topic_aruco = str(self.get_parameter('topic_aruco').value)
        self.sub_aruco = self.create_subscription(
            String, topic_aruco, self.callback_aruco, 10
        )

        # Estados secuenciales: 
        self.estado = 'IR_PUERTA'
        self.meta_enviada = False
        self.nav2_listo = False
        self.aruco_leido = None
        self.destino_asignado = None
        self.ticks_busqueda = 0

        self.timer = self.create_timer(0.1, self.callback_maquina_estados)
        self.get_logger().info('Nodo autonomous_navigation inicializado correctamente.')
        self.get_logger().info(f'Escuchando detector en {topic_aruco}.')

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

    def callback_aruco(self, msg: String):
        if self.estado != 'LEER_ARUCO':
            return
        if self.aruco_leido is not None and self.destino_asignado is not None:
            return

        texto = msg.data.strip()
        if not texto:
            return

        match_id = re.search(r'\bID\s*:\s*(\d+)\b', texto, re.IGNORECASE)
        if match_id:
            candidatos = [int(match_id.group(1))]
        else:
            candidatos = [int(n) for n in re.findall(r'\b\d+\b', texto)]

        destinos = self.obtener_destinos()
        for marker_id in candidatos:
            if marker_id in destinos:
                dx, dy, dyaw = destinos[marker_id]
                self.aruco_leido = marker_id
                self.destino_asignado = (dx, dy, dyaw)
                self.get_logger().info(
                    f'ArUco detectado ID={marker_id} | Coordenada predefinida asignada: '
                    f'x={dx:.2f}, y={dy:.2f}, yaw={dyaw:.2f}'
                )
                break

    def callback_maquina_estados(self):
        # ESTADO 1: IR A LA PUERTA
        if self.estado == 'IR_PUERTA':
            if not self.nav2_listo:
                ix = float(self.get_parameter('initial_x').value)
                iy = float(self.get_parameter('initial_y').value)
                iyaw = float(self.get_parameter('initial_yaw').value)
                self.get_logger().info(f'Pose inicial: ({ix}, {iy}, {iyaw})')
                self.navigator.setInitialPose(self.crear_pose_stamped(ix, iy, iyaw))
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

        # ESTADO 2: LEER EL ARUCO DESDE EL DETECTOR
        elif self.estado == 'LEER_ARUCO':
            if self.aruco_leido is not None and self.destino_asignado is not None:
                self.estado = 'IR_DESTINO'
                self.meta_enviada = False
            else:
                self.ticks_busqueda += 1
                if self.ticks_busqueda % 20 == 0:
                    self.get_logger().info('Esperando deteccion de ArUco desde el nodo detector...')

        # ESTADO 3: IR A LA COORDENADA META ASIGNADA
        elif self.estado == 'IR_DESTINO':
            if not self.meta_enviada:
                dx, dy, dyaw = self.destino_asignado
                self.get_logger().info(
                    f'ArUco ID {self.aruco_leido} -> Navegando a destino final ({dx}, {dy}, {dyaw})'
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
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
