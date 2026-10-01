import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger
from turtlesim.srv import SetPen
import time

#from .numero_1 import obtener_trazos_uno
#from .numero_5 import obtener_trazos_cinco

class ControladorTortugaG15(Node):
    def __init__(self):
        super().__init__('controlador_tortuga_g15')
        self.publicador_velocidad = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.servicio_control = self.create_service(Trigger, 'pausar_reanudar_dibujo', self.cb_servicio_control)
        self.cliente_lapiz = self.create_client(SetPen, '/turtle1/set_pen')
        self.lapiz_levantado = False
        self.timer = self.create_timer(0.1, self.cb_bucle_principal)
        self.en_pausa = False
        self.trazos = [
            {"lineal": 2.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False},
            {"lineal": 0.0, "angular": -1.5, "duracion": 0.5, "levantar_lapiz": True}
        ]
        self.indice_actual = 0
        self.tiempo_inicio_trazo = None

        self.get_logger().info('Nodo del Grupo 15 iniciado. Tortuga lista para dibujar.')

    def cb_servicio_control(self, request, response):
        self.en_pausa = not self.en_pausa
        
        if self.en_pausa:
            mensaje = "Tortuga pausada..."
            msg_parada = Twist()
            self.publicador_velocidad.publish(msg_parada)
        else:
            mensaje = "Tortuga reanudada..."
            if self.tiempo_inicio_trazo is not None:
                self.tiempo_inicio_trazo = time.time()
                
        self.get_logger().info(mensaje)
        response.success = True
        response.message = mensaje
        return response

    def cb_bucle_principal(self):
        if self.en_pausa:
            return
            
        if self.indice_actual >= len(self.trazos):
            self.get_logger().info('Dibujo finalizado.', once=True)
            msg_parada = Twist()
            self.publicador_velocidad.publish(msg_parada)
            return

        if self.tiempo_inicio_trazo is None:
            self.tiempo_inicio_trazo = time.time()
            self.get_logger().info(f'Iniciando trazo {self.indice_actual + 1} de {len(self.trazos)}')

        trazo_actual = self.trazos[self.indice_actual]
        lineal = trazo_actual["lineal"]
        angular = trazo_actual["angular"]
        duracion = trazo_actual["duracion"]
        levantar_lapiz = trazo_actual["levantar_lapiz"]
        
        if levantar_lapiz != self.lapiz_levantado:
            req = SetPen.Request()
            req.r, req.g, req.b = 255, 255, 255
            req.width = 3
            req.off = 1 if levantar_lapiz else 0 
            self.cliente_lapiz.call_async(req)
            self.lapiz_levantado = levantar_lapiz
        
        tiempo_transcurrido = time.time() - self.tiempo_inicio_trazo
        
        if tiempo_transcurrido < duracion:
            msg = Twist()
            msg.linear.x = float(lineal)
            msg.angular.z = float(angular)
            self.publicador_velocidad.publish(msg)
        else:
            self.tiempo_inicio_trazo = None
            self.indice_actual += 1

def main(args=None):
    rclpy.init(args=args)
    nodo_g15 = ControladorTortugaG15()
    rclpy.spin(nodo_g15)
    nodo_g15.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
