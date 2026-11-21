#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


class PredefinedNavigation(Node):
    def __init__(self):
        super().__init__('predefined_navigation')

        # ParSmetros editar Valeria
        self.declare_parameter('goal_x', 4.5)
        self.declare_parameter('goal_y', 1.2)
        self.declare_parameter('goal_yaw', 0.0)

        self.navigator = BasicNavigator()
        self.goal_sent = False

        # Timer de revision
        self.timer = self.create_timer(0.5, self.timer_callback)

    def crear_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def timer_callback(self):
        if not self.goal_sent: #no se ha enviado la meta
            self.get_logger().info('Esperando a que Nav2 se activo...')
            self.navigator.waitUntilNav2Active()
            x = self.get_parameter('goal_x').value
            y = self.get_parameter('goal_y').value
            yaw = self.get_parameter('goal_yaw').value
            self.get_logger().info(f'Enviando meta: ({x}, {y}, {yaw})')
            self.navigator.goToPose(self.crear_pose(x, y, yaw))
            self.goal_sent = True
            return

        if self.navigator.isTaskComplete(): #cuando ya ha  terminado la tarea
            if self.navigator.getResult() == TaskResult.SUCCEEDED:
                self.get_logger().info('Llegada al punto predefinido completada')
            else:
                self.get_logger().warn('No se pudo alcanzar el punto predefinido')
            self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = PredefinedNavigation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.navigator.cancelTask()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
