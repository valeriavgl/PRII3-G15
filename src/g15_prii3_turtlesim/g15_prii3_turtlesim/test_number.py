import rclpy
from turtlesim_msgs.srv import SetPen
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
from number_five import *
from number_one import *



class MiniMotor(Node):
    def __init__(self):
        super().__init__('mini_motor')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10) 

        #parametros del publisher
        #Twist tipo de dato que sera trasnmitido que sera par velocidad en un espacion tridimensional 
        #turtle1 nombre del canal
        #cmd_vel: comando velocidad = frecuencia de radio
        # 10 tmaño de la cola


    def actualizar_lapiz(self, levantar):
        # Creacion del cliente para el servicio si no existe
        cliente = self.create_client(SetPen, '/turtle1/set_pen')
        
        # Espera del servicio esté disponible (máximo 1 segundo para no congelar el nodo)
        if not cliente.wait_for_service(timeout_sec=1.0):
            self.get_logger().error('El servicio /turtle1/set_pen no está disponible')
            return

        # Creacion de la solicitud con los parámetros
        peticion = SetPen.Request()
        peticion.r = 255
        peticion.g = 255
        peticion.b = 255
        peticion.width = 3
        peticion.off = 1 if levantar else 0

        # Llamada del servicio de forma asíncrona (no bloquea el código)
        cliente.call_async(peticion)


    def ejecutar(self, rutina):
        time.sleep(1.0) # Pausa inicial
        for paso in rutina:
            print(f"Ejecutando: {paso}")
            #paso de parametro del diccioneario 

            #revisa si se debe levantar el lapiz o no 
            self.actualizar_lapiz(paso["levantar_lapiz"]) 
            #Tipo de dato a enviar en el mensaje
            msg = Twist()
            # Velocidad linal
            msg.linear.x = float(paso["lineal"])
            # Velocidad angular
            msg.angular.z = float(paso["angular"])
            #Publicacion del mensaje
            self.publisher.publish(msg)
            #duracion del comando
            time.sleep(paso["duracion"])
            #Creacion de mensaje de velocidad nuevo sin parametros, para frenar
            self.publisher.publish(Twist()) 
            time.sleep(0.2)

def main(args=None):
    rclpy.init(args=args)
    motor = MiniMotor()


    
    print("¡Enviando instrucciones a la super tortuga!")
    motor.ejecutar(get_initial_moves())
    motor.ejecutar(get_moves_for_one())
    motor.ejecutar(get_moves_for_five())
    motor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()