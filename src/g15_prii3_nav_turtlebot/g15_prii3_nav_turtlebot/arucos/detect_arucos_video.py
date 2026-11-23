import cv2 as cv
import cv2.aruco as aruco
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


#configuracion inciial: Camara a usar, ruta del archivo de calibracion, y el tamaño de los marcadores
CALIB_PATH = "/home/alexa/g15_prii3_ws/camera/calibration/calibracion_camara.yml"
MARKER_SIZE = 0.1  # metros

def extract_yml(path_doc):
#Se abre el .yml pasandole la ruta y el modo (en este caso lectura) 
    p_file = cv.FileStorage(path_doc, cv.FILE_STORAGE_READ)

    if not p_file.isOpened():
        print(" No se pudo abrir el archivo de calibración.")
        exit()

    #Extraemos los parametros del archivo .yml
    #La función getNode() busca la etiqueta en el .yml y .mat() la convierte a un array 
    cameraMatrix = p_file.getNode("cameraMatrix").mat()
    distCoeffs = p_file.getNode("distCoeffs").mat()
    #Cerrar Archivo
    p_file.release()

    return (cameraMatrix, distCoeffs)

class ArucoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')
        self.bridge = CvBridge()

        # Parámetros configurables
        #tópico del que se reciben las imágenes de la cámara
        self.declare_parameter('topic_camara', '/camera/image_raw')
        # tópico por donde se publicarán los IDs y coordenadas
        self.declare_parameter('topic_salida', '/arucos')
        # Tiempo en segundos entre cada publicación del temporizador
        self.declare_parameter('periodo', 0.5)
        # Ruta al archivo .yml con los parámetros de calibración de la cámara
        self.declare_parameter('calib_path', CALIB_PATH)
        # Tamaño real del lado del marcador ArUco en metros
        self.declare_parameter('marker_size', MARKER_SIZE)
        #asigancion de parametros
        topic_camara = self.get_parameter('topic_camara').value
        topic_salida = self.get_parameter('topic_salida').value
        periodo = float(self.get_parameter('periodo').value)
        calib_path = self.get_parameter('calib_path').value
        self.marker_size = float(self.get_parameter('marker_size').value)

        #Cargar calibración desde el archivo .yml
        self.cameraMatrix, self.distCoeffs = extract_yml(calib_path)

        # Configurar la deteccion de ArUcos (DICT_4X4_100)
        diccionario = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
        self.detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())
        self.obj_points = np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=np.float32) * (self.marker_size/ 2.0)

        # Texto con los últimos ArUcos detectados
        self.text = ""

        # Suscriptor a la cámara, publicador del topico de salida y creacion del temporizador
        self.create_subscription(Image, topic_camara, self.callback_imagen, 10)
        self.pub = self.create_publisher(String, topic_salida, 10)
        self.create_timer(periodo, self.callback_topico_aruco)
        #muestra por terminal por el topico que esta escuhando y por donde esta publicando al info de los Arucos
        self.get_logger().info(f'Escuchando {topic_camara} y publicando en {topic_salida}')

    def callback_imagen(self, msg):
        # Convertir imagen de ROS 2 a OpenCV
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # Rectificación de imagen con los parámetros del .yml
        image_rect = cv.undistort(image, self.cameraMatrix, self.distCoeffs)
        # Buscar los marcadores en la imagen rectificada
        corners, ids, _ = self.detector.detectMarkers(image_rect)
        detectados = []

        if ids is not None:
            # Recorre cada marcador encontrado individualmente para calcular su posición 3D.
            for i in range(len(ids)):
            # solvePnP: Calcula la rotación (rvec) y la distancia/posición (tvec) del marcador.
                _, rvec, tvec = cv.solvePnP(self.obj_points, corners[i][0], self.cameraMatrix, None)
                id_aruco = ids[i][0]
                x, y, z = tvec[0][0], tvec[1][0], tvec[2][0]
                detectados.append(f"ID:{id_aruco} (X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f})")
        # Si no hay ArUcos visibles, queda vacío ""
        self.text = " | ".join(detectados)

    def callback_topico_aruco(self):
        msg = String()
        #últimos ArUcos detectados
        msg.data = self.text
        # Publica el mensaje en el tópico Aruco
        self.pub.publish(msg)
            
def main(args=None):
    rclpy.init(args=args)
    # Crea el nodo instanciando la clase ArucoDetector
    nodo = ArucoDetector()
    try:
        # Mantiene el nodo activo escuchando la cámara y ejecutando el temporizador
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        # Destruye el nodo
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()