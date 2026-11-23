#!/usr/bin/env python3
import cv2                                    
import rclpy                                  
from rclpy.node import Node                   
from sensor_msgs.msg import Image             
from std_msgs.msg import String               
from cv_bridge import CvBridge                


class ArucoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')    

        self.declare_parameter('topic_camara', '/camera/image_raw')
        self.declare_parameter('topic_salida', '/aruco_detections')    
        self.declare_parameter('topic_debug', '/aruco_debug')          
        self.declare_parameter('periodo_publicacion', 0.1)             

        self.bridge = CvBridge()              

        # Detector con el diccionario
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
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

        # Suscriptor:
        topic_camara = self.get_parameter('topic_camara').value
        self.sub_imagen = self.create_subscription(
            Image, topic_camara, self.callback_imagen, 1
        )

        # Publicadores
        self.pub_ids = self.create_publisher(
            String, self.get_parameter('topic_salida').value, 10
        )
        self.pub_debug = self.create_publisher(
            Image, self.get_parameter('topic_debug').value, 1
        )

        self.ultimo_envio = 0.0               
        self.get_logger().info('Nodo aruco_detector listo. Esperando imagenes de la camara...')

    #  CALLBACK 
    def callback_imagen(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')   
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                   
            esquinas, ids, _ = self._detectar_aruco(gray)                     

            if ids is not None:                                               
                cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)           
                lista_ids = [int(i) for i in ids.flatten()]                   

                ahora = self.get_clock().now().nanoseconds / 1e9              
                periodo = float(self.get_parameter('periodo_publicacion').value)
                if ahora - self.ultimo_envio >= periodo:                      
                    self.ultimo_envio = ahora
                    texto = String()
                    texto.data = ','.join(str(i) for i in lista_ids)          
                    self.pub_ids.publish(texto)                               
                    self.get_logger().info(f'ArUco detectado: {lista_ids}')

                salida = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')        
                salida.header = msg.header                                        
                self.pub_debug.publish(salida)                                    
        except Exception as e:                                                
            self.get_logger().error(f'Error procesando imagen: {e}')



def main(args=None):
    rclpy.init(args=args)                       
    nodo = ArucoDetector()                      
    try:
        rclpy.spin(nodo)                        
    except KeyboardInterrupt:                   
        pass
    finally:
        nodo.destroy_node()                     
        rclpy.shutdown()                        


if __name__ == '__main__':
    main()
