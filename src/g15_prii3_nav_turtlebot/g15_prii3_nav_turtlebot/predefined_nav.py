import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# (x, y, angulo_en_grados)
pos_inicial = (-2.06, -11.79, 0)     # Pasillo 
pos_final = (-0.22, 2.00, 90)     # Laboratorio 

class PredefinedNavigation(Node):
    def __init__(self):
        # Inicio de nodo y Nav2
        super().__init__('predefined_navigation')
        self.navigator = BasicNavigator()

    def crear_posicion(self, x, y, grados=0):
        #convertimos de grados a radianes
        yaw =math.radians(grados)
        #variable con formato para ROS2 para posicion y orientacion 
        pose = PoseStamped()
        #coordenadas de tipo map (x, y)
        pose.header.frame_id = 'map'
        #marca el tiempo de cuando se genero la posicion
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        #asignacion de parametros para la posicion
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
         #calculo de Z
        pose.pose.orientation.z = math.sin(yaw / 2.0)
         #calculo de W
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        return pose

    def ejecutar(self):
        #Posicion inicial
        #Muestra por terminal las coordenadas guardadas, es decir, la posicion inicial
        self.get_logger().info(f'Pose inicial: {pos_inicial}')
        #Indica el punto de inicio del robot en el  mapa
        self.navigator.setInitialPose(self.crear_posicion(*pos_inicial))
        #Pausa hasta que nav2 y la AMCL esten arrancados 
        self.navigator.waitUntilNav2Active()

        # Posicion final
        self.get_logger().info(f'Navegando al destino: {pos_final}')
        #Orden para calcular la ruta al destino 
        self.navigator.goToPose(self.crear_posicion(*pos_final))

        #Se queda en bucle hasta que Nav2 avise de que la tarea ha terminado
        while not self.navigator.isTaskComplete():
            pass

        #comprueba que haya llegado correctamente
        if self.navigator.getResult() == TaskResult.SUCCEEDED:
            self.get_logger().info('Posición final alcanzada')
        else:
            #Si hubo algun problema lo muestra por terminal
            self.get_logger().warn(f'Navegación terminada con estado: {self.navigator.getResult()}')

def main(args=None):
    #Inicio de ROS2
    rclpy.init(args=args)
    #Crea el nodo instanciando la clase
    nodo = PredefinedNavigation()
    try:
        nodo.ejecutar()
    except KeyboardInterrupt:
        nodo.navigator.cancelTask()
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()