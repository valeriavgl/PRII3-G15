import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger, SetBool, Empty
import time

from .number_one import get_moves_for_one
from .number_five import get_moves_for_five

class ControladorJetbotG15(Node):
    def __init__(self):
        super().__init__('controlador_JetBot_g15')
        self.publicador_velocidad = self.create_publisher(Twist, '/cmd_vel', 10)
        
        
        # --- SERVICIOS SOLICITADOS ---
        self.servicio_marcha = self.create_service(SetBool, 'control_dibujo', self.servicio_marcha_callback)
        self.servicio_reiniciar = self.create_service(Trigger, 'reiniciar_dibujo', self.servicio_reiniciar_callback)

        self.timer = self.create_timer(0.1, self.bucle_principal_callback)
        self.en_pausa = False
        
        self.trazos =  get_moves_for_one() + get_moves_for_five()
        self.i = 0
        self.tiempo_inicio_trazo = None
        self.instante_pausa = 0.0

        self.get_logger().info('Nodo del Grupo 15 iniciado. Estado: Dibujando.')

    def servicio_marcha_callback(self, request, response):
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
            mensaje = f"El JetBot ya estaba en el estado solicitado (En pausa: {self.en_pausa})."

        self.get_logger().info(mensaje)
        response.success = True
        response.message = mensaje
        return response

    def servicio_reiniciar_callback(self, request, response):
        """Maneja el reinicio del dibujo"""
        msg_parada = Twist()
        self.publicador_velocidad.publish(msg_parada)

        self.i = 0 
        self.tiempo_inicio_trazo = None

        self.en_pausa = False
        self.i = 0
        self.tiempo_inicio_trazo = None
        self.instante_pausa = 0.0
        
        mensaje = "DIBUJO REINICIADO. Comenzando desde el primer trazo."
        self.get_logger().warn(mensaje)
        
        response.success = True
        response.message = mensaje
        return response

    def bucle_principal_callback(self):
        if self.en_pausa:
            return
            
        if self.i >= len(self.trazos):
            self.get_logger().info('Dibujo finalizado.', once=True)
            msg_parada = Twist()
            self.publicador_velocidad.publish(msg_parada)
            return

        if self.tiempo_inicio_trazo is None:
            self.tiempo_inicio_trazo = time.time()
            self.get_logger().info(f'Iniciando trazo {self.i + 1} de {len(self.trazos)}')

        trazo_actual = self.trazos[self.i]
        lineal = trazo_actual["lineal"]
        angular = trazo_actual["angular"]
        duracion = trazo_actual["duracion"]
        
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
            self.i += 1

def main(args=None):
    rclpy.init(args=args)
    nodo_g15 = ControladorJetbotG15()
    try:
        rclpy.spin(nodo_g15)
    except KeyboardInterrupt:
        pass
    finally:
        nodo_g15.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()