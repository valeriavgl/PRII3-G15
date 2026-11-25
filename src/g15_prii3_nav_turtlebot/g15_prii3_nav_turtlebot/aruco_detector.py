import cv2 as cv
import cv2.aruco as aruco
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


CALIB_PATH = "/home/alexa/g15_prii3_ws/camera/calibration/calibracion_camara.yml"
MARKER_SIZE = 0.1


def extract_yml(path_doc):
    p_file = cv.FileStorage(path_doc, cv.FILE_STORAGE_READ)
    if not p_file.isOpened():
        return None, None
    cameraMatrix = p_file.getNode("cameraMatrix").mat()
    distCoeffs = p_file.getNode("distCoeffs").mat()
    p_file.release()
    if cameraMatrix is None or distCoeffs is None:
        return None, None
    return cameraMatrix, distCoeffs


class ArucoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')
        self.bridge = CvBridge()

        self.declare_parameter('topic_camara', '/camera/image_raw')
        self.declare_parameter('topic_salida', '/arucos')
        self.declare_parameter('periodo', 0.5)
        self.declare_parameter('calib_path', CALIB_PATH)
        self.declare_parameter('marker_size', MARKER_SIZE)

        topic_camara = self.get_parameter('topic_camara').value
        topic_salida = self.get_parameter('topic_salida').value
        periodo = float(self.get_parameter('periodo').value)
        calib_path = self.get_parameter('calib_path').value
        self.marker_size = float(self.get_parameter('marker_size').value)

        self.cameraMatrix, self.distCoeffs = extract_yml(calib_path)
        if self.cameraMatrix is None:
            self.get_logger().warn(
                f'No se pudo cargar calibracion desde {calib_path}. Se continuara sin rectificacion.'
            )

        diccionario = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
        if hasattr(aruco, 'ArucoDetector'):
            self._detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())
            self._detectar = lambda gray: self._detector.detectMarkers(gray)
        else:
            self._params = aruco.DetectorParameters_create()
            self._detectar = lambda gray: aruco.detectMarkers(
                gray, diccionario, parameters=self._params
            )

        self.obj_points = (
            np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=np.float32) * (self.marker_size / 2.0)
        )

        self.text = ""

        self.create_subscription(Image, topic_camara, self.callback_imagen, 10)
        self.pub = self.create_publisher(String, topic_salida, 10)
        self.create_timer(periodo, self.callback_topico_aruco)
        self.get_logger().info(f'Escuchando {topic_camara} y publicando en {topic_salida}')

    def callback_imagen(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        if self.cameraMatrix is not None and self.distCoeffs is not None:
            image_proc = cv.undistort(image, self.cameraMatrix, self.distCoeffs)
        else:
            image_proc = image

        corners, ids, _ = self._detectar(image_proc)
        detectados = []

        if ids is not None:
            for i in range(len(ids)):
                id_aruco = int(ids[i][0])
                if self.cameraMatrix is not None:
                    _, rvec, tvec = cv.solvePnP(
                        self.obj_points, corners[i][0], self.cameraMatrix, None
                    )
                    x, y, z = float(tvec[0][0]), float(tvec[1][0]), float(tvec[2][0])
                    detectados.append(f"ID:{id_aruco} (X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f})")
                else:
                    detectados.append(f"ID:{id_aruco}")

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
