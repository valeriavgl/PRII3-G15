import cv2 as cv
import cv2.aruco as aruco
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import String
from cv_bridge import CvBridge


# Configuracion inicial
CALIB_PATH = "/home/nmquiana/Documents/Proyecto3/PRII3-G15/camera/calibration/calibracion_camara.yml"
MARKER_SIZE = 0.1  # metros


def extract_yml(path_doc):
    p_file = cv.FileStorage(path_doc, cv.FILE_STORAGE_READ)

    if not p_file.isOpened():
        return None, None

    cameraMatrix = p_file.getNode("cameraMatrix").mat()
    distCoeffs = p_file.getNode("distCoeffs").mat()
    p_file.release()

    return cameraMatrix, distCoeffs


class ArucoDetector(Node):

    def __init__(self):
        super().__init__('aruco_detector')
        self.bridge = CvBridge()

        # Parametros configurables
        self.declare_parameter('topic_camara', '/camera/image_raw')
        self.declare_parameter('topic_salida', '/arucos')
        self.declare_parameter('periodo', 0.5)
        self.declare_parameter('calib_path', CALIB_PATH)
        self.declare_parameter('marker_size', MARKER_SIZE)
        self.declare_parameter('dictionary', 'DICT_5X5_100')
        self.declare_parameter('usar_camera_info', True)

        topic_camara = self.get_parameter('topic_camara').value
        topic_salida = self.get_parameter('topic_salida').value
        periodo = float(self.get_parameter('periodo').value)
        calib_path = self.get_parameter('calib_path').value
        self.marker_size = float(self.get_parameter('marker_size').value)
        dict_name = self.get_parameter('dictionary').value
        self.usar_camera_info = self.get_parameter('usar_camera_info').value

        # Calibracion de la camara
        self.cameraMatrix = None
        self.distCoeffs = None

        if self.usar_camera_info:
            self.create_subscription(
                CameraInfo, '/camera/camera_info',
                self.callback_camera_info, qos_profile_sensor_data
            )
        else:
            self.cameraMatrix, self.distCoeffs = extract_yml(calib_path)

            if self.cameraMatrix is None:
                self.get_logger().error('No se pudo cargar la calibracion YAML.')

        # Configuracion del diccionario ArUco
        diccionario = aruco.getPredefinedDictionary(
            getattr(aruco, dict_name)
        )

        if hasattr(aruco, 'ArucoDetector') and hasattr(aruco, 'DetectorParameters'):
            params = aruco.DetectorParameters()
            detector = aruco.ArucoDetector(diccionario, params)
            self.detector = lambda img: detector.detectMarkers(img)
        else:
            params = aruco.DetectorParameters_create()
            self.detector = lambda img: aruco.detectMarkers(
                img, diccionario, parameters=params
            )

        # Esquinas 3D del marcador
        self.obj_points = np.array(
            [[-1, 1, 0], [1, 1, 0],
             [1, -1, 0], [-1, -1, 0]],
            dtype=np.float32
        ) * (self.marker_size / 2.0)

        self.text = ""

        # Suscripcion, publicador y temporizador
        self.create_subscription(
            Image, topic_camara, self.callback_imagen,
            qos_profile_sensor_data
        )
        self.pub = self.create_publisher(String, topic_salida, 10)
        self.create_timer(periodo, self.callback_topico_aruco)

        self.get_logger().info(
            f'Escuchando {topic_camara} y publicando en {topic_salida}'
        )

    def callback_camera_info(self, msg):
        self.cameraMatrix = np.array(msg.k).reshape(3, 3)
        self.distCoeffs = np.array(msg.d)

    def callback_imagen(self, msg):
        image = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding='bgr8'
        )

        # Conversion a escala de grises
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Deteccion de ArUcos
        corners, ids, _ = self.detector(gray)

        detectados = []

        if ids is not None:
            if self.cameraMatrix is None or self.distCoeffs is None:
                self.text = ""
                return

            for i in range(len(ids)):
                resultado, rvec, tvec = cv.solvePnP(
                    self.obj_points,
                    corners[i][0],
                    self.cameraMatrix,
                    self.distCoeffs
                )

                if resultado:
                    id_aruco = int(ids[i][0])
                    x, y, z = tvec.flatten()

                    detectados.append(
                        f"ID:{id_aruco} (X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f})"
                    )

        self.text = " | ".join(detectados)

    def callback_topico_aruco(self):
        msg = String()
        msg.data = self.text
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    nodo = ArucoDetector()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
