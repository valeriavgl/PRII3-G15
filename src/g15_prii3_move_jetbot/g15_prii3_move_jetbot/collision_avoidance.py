#!/usr/bin/env python3

# ===== 1. IMPORTACIONES =====
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool


# ===== 2. CLASE =====
class CollisionAvoidance(Node):

    # ===== 3. CONSTRUCTOR =====
    def __init__(self):
        super().__init__('collision_avoidance')

        self.distancia_parada = 0.5   # Distancia mínima permitida (m)
        self.angulo_frente = 30.0     # grados a cada lado del frente
        self.pausado = False          # estado del dibujo que conocemos
        self.llamando = False         # hay una llamada al servicio en curso

        self.sub = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, qos_profile_sensor_data)
        self.cliente = self.create_client(SetBool, 'control_dibujo')

    # ===== 4. CALLBACKS Y FUNCIONES =====
    def scan_callback(self, msg):
        limite = math.radians(self.angulo_frente) #traduccion a radianes
        frente = [] # guardar distancias de objetos detectables
        for i, r in enumerate(msg.ranges): # i rayo, r distancia
            angulo = msg.angle_min + i * msg.angle_increment # Calcula a qué ángulo corresponde este rayo exacto
            #conversion del angulo a coordenadas y luego con el arcotangente limitamos al rango de -180 a 180 grados 
            angulo = math.atan2(math.sin(angulo), math.cos(angulo)) 
            if abs(angulo) <= limite and msg.range_min < r < msg.range_max: # el rayo esta en el perimetro de mi via 
                frente.append(r)
        obstaculo = len(frente) > 0 and min(frente) < self.distancia_parada

        if obstaculo and not self.pausado:
            self.enviar(False)    # detener el dibujo
        elif not obstaculo and self.pausado:
            self.enviar(True)     # reanudar el dibujo

    def enviar(self, seguir):
        if self.llamando or not self.cliente.service_is_ready():
            return
        self.llamando = True
        peticion = SetBool.Request()
        peticion.data = seguir
        futuro = self.cliente.call_async(peticion)
        futuro.add_done_callback(lambda f: self.respuesta(f, seguir))

    def respuesta(self, futuro, seguir):
        self.llamando = False
        resultado = futuro.result()
        if resultado is not None and resultado.success:
            self.pausado = not seguir
            self.get_logger().info(resultado.message)


# ===== 5. MAIN =====
def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
