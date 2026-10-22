import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger, SetBool, Empty
from turtlesim.srv import SetPen, TeleportAbsolute
import time

from .number_one import get_moves_for_one, get_initial_moves
from .number_five import get_moves_for_five

class ControladorTortugaG15(Node):
    def __init__(self):
        super().__init__('controlador_tortuga_g15')
        self.publicador_velocidad = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # --- SERVICIOS SOLICITADOS ---
        self.servicio_marcha = self.create_service(SetBool, 'control_dibujo', self.cb_servicio_marcha)
        self.servicio_reiniciar = self.create_service(Trigger, 'reiniciar_dibujo', self.cb_servicio_reiniciar)
        self.cliente_lapiz = self.create_client(SetPen, '/turtle1/set_pen')
        self.cliente_teleport = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.cliente_limpiar = self.create_client(Empty, '/clear')
        
        while not self.cliente_lapiz.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando a que la tortuga despierte...')
            
        self.lapiz_levantado = False
        self.timer = self.create_timer(0.01, self.cb_bucle_principal)
        self.en_pausa = False
        
        self.trazos = get_initial_moves() + get_moves_for_one() + get_moves_for_five()
        self.indice_actual = 0
        self.tiempo_inicio_trazo = None
        self.instante_pausa = 0.0

        self.get_logger().info('Nodo del Grupo 15 iniciado. Estado: Dibujando.')

    def cb_servicio_marcha(self, request, response):
        """Maneja la detención y la reanudación mediante un booleano (True=Reanudar, False=Detener)"""
        seguir = request.data
        
        if not seguir and not self.en_pausa:
            self.en_pausa = True
            msg_parada = Twist()
            self.publicador_velocidad.publish(msg_parada)
            self.instante_pausa = time.time()
            mensaje = "Tortuga DETENIDA por servicio."
        elif seguir and self.en_pausa:
            self.en_pausa = False
            if self.tiempo_inicio_trazo is not None:
                tiempo_detenida = time.time() - self.instante_pausa
                self.tiempo_inicio_trazo += tiempo_detenida
            mensaje = "Tortuga REANUDADA por servicio."
        else:
            mensaje = f"La tortuga ya estaba en el estado solicitado (En pausa: {self.en_pausa})."

        self.get_logger().info(mensaje)
        response.success = True
        response.message = mensaje
        return response

    def cb_servicio_reiniciar(self, request, response):
        """Maneja el reinicio del dibujo"""
        msg_parada = Twist()
        self.publicador_velocidad.publish(msg_parada)
        
        req_teleport = TeleportAbsolute.Request()
        req_teleport.x = 5.544445
        req_teleport.y = 5.544445
        req_teleport.theta = 0.0
        self.cliente_teleport.call_async(req_teleport)
        req_limpiar = Empty.Request()
        self.cliente_limpiar.call_async(req_limpiar)

        req_pen = SetPen.Request()
        req_pen.r, req_pen.g, req_pen.b = 255, 255, 255
        req_pen.width = 3
        req_pen.off = 1
        self.cliente_lapiz.call_async(req_pen)
        
        time.sleep(0.5)

        self.en_pausa = False
        self.indice_actual = 0
        self.tiempo_inicio_trazo = None
        self.instante_pausa = 0.0
        self.lapiz_levantado = True
        
        mensaje = "DIBUJO REINICIADO. Comenzando desde el primer trazo."
        self.get_logger().warn(mensaje)
        
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
            msg_parada = Twist()
            self.publicador_velocidad.publish(msg_parada)
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