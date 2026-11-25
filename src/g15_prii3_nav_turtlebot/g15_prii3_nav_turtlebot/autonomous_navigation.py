#!/usr/bin/env python3
import math
import re
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

DEFAULT_DESTINOS = [
    (5, 1.2, -3.3, 0.0),
    (6, -2.8, -2.4, 1.57),
    (17, -2.3, -2.2, -1.57),
]


class AutonomousNavigation(Node):

    def __init__(self):
        super().__init__('autonomous_navigation')

        self.declare_parameter('topic_aruco', '/arucos')
        for nombre, valor in [
            ('initial_x', -2.06), ('initial_y', -11.79), ('initial_yaw', 0.0),
            ('puerta_x', 0.78), ('puerta_y', -10.10), ('puerta_yaw', 1.77),
        ]:
            self.declare_parameter(nombre, valor)

        for idx, (marker_id, x, y, yaw) in enumerate(DEFAULT_DESTINOS, start=1):
            self.declare_parameter(f'id_aruco_{idx}', marker_id)
            self.declare_parameter(f'dest{idx}_x', x)
            self.declare_parameter(f'dest{idx}_y', y)
            self.declare_parameter(f'dest{idx}_yaw', yaw)

        self.navigator = BasicNavigator()
        topic_aruco = str(self.get_parameter('topic_aruco').value)
        self.create_subscription(String, topic_aruco, self.callback_aruco, 10)

        self.estado = 'IR_PUERTA'
        self.meta_enviada = False
        self.nav2_listo = False
        self.aruco_leido = None
        self.destino_asignado = None
        self.ticks_busqueda = 0

        self.timer = self.create_timer(0.1, self.callback_maquina_estados)
        self.get_logger().info(f'Nodo listo. Escuchando {topic_aruco}.')

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
        destinos = {}
        for idx in range(1, len(DEFAULT_DESTINOS) + 1):
            marker_id = int(self.get_parameter(f'id_aruco_{idx}').value)
            destinos[marker_id] = (
                float(self.get_parameter(f'dest{idx}_x').value),
                float(self.get_parameter(f'dest{idx}_y').value),
                float(self.get_parameter(f'dest{idx}_yaw').value),
            )
        return destinos

    def callback_aruco(self, msg: String):
        if self.estado != 'LEER_ARUCO' or self.destino_asignado is not None:
            return

        candidatos = [
            int(n) for n in re.findall(r'\bID\s*:\s*(\d+)\b', msg.data, re.IGNORECASE)
        ]
        destinos = self.obtener_destinos()

        for marker_id in candidatos:
            if marker_id in destinos:
                self.aruco_leido = marker_id
                self.destino_asignado = destinos[marker_id]
                dx, dy, dyaw = self.destino_asignado
                self.get_logger().info(
                    f'ArUco ID={marker_id} -> destino x={dx:.2f}, y={dy:.2f}, yaw={dyaw:.2f}'
                )
                break

    def enviar_meta_y_esperar(self, x: float, y: float, yaw: float, msg_inicio: str):
        if not self.meta_enviada:
            self.get_logger().info(f'{msg_inicio}: ({x}, {y}, {yaw})')
            self.navigator.goToPose(self.crear_pose_stamped(x, y, yaw))
            self.meta_enviada = True
            return None

        if not self.navigator.isTaskComplete():
            return None

        self.meta_enviada = False
        return self.navigator.getResult() == TaskResult.SUCCEEDED

    def callback_maquina_estados(self):
        if self.estado == 'IR_PUERTA':
            if not self.nav2_listo:
                ix = float(self.get_parameter('initial_x').value)
                iy = float(self.get_parameter('initial_y').value)
                iyaw = float(self.get_parameter('initial_yaw').value)
                self.get_logger().info(f'Pose inicial: ({ix}, {iy}, {iyaw})')
                self.navigator.setInitialPose(self.crear_pose_stamped(ix, iy, iyaw))
                self.navigator.waitUntilNav2Active()
                self.nav2_listo = True

            ok = self.enviar_meta_y_esperar(
                float(self.get_parameter('puerta_x').value),
                float(self.get_parameter('puerta_y').value),
                float(self.get_parameter('puerta_yaw').value),
                'Yendo a la puerta',
            )
            if ok is True:
                self.get_logger().info('Llegada a la puerta. Buscando ArUco...')
                self.estado = 'LEER_ARUCO'
            elif ok is False:
                self.get_logger().error('Fallo al llegar a la puerta.')
                self.estado = 'FIN'
                self.timer.cancel()

        elif self.estado == 'LEER_ARUCO':
            if self.destino_asignado is not None:
                self.estado = 'IR_DESTINO'
            else:
                self.ticks_busqueda += 1
                if self.ticks_busqueda % 20 == 0:
                    self.get_logger().info('Esperando deteccion de ArUco...')

        elif self.estado == 'IR_DESTINO':
            dx, dy, dyaw = self.destino_asignado
            ok = self.enviar_meta_y_esperar(
                dx, dy, dyaw, f'ArUco ID {self.aruco_leido} -> destino final'
            )
            if ok is not None:
                if ok:
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