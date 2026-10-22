import cv2 as cv
import cv2.aruco as aruco
import argparse
import numpy as np

def extract_yml(path_doc):
    
#Se abre el .yml pasandole la ruta y el modo (en este caso lectura) 
    p_file = cv.FileStorage(path_doc, cv.FILE_STORAGE_READ)

    if not p_file.isOpened():
        print(" No se pudo abrir el archivo de calibración.")
        exit()

    #Extraemos los parametros del archivo .yml
    #La función getNode() busca la etiqueta en el .yml y .mat() la convierte a un formato que OpenCV puede usar (NumPy array)
    cameraMatrix = p_file.getNode("cameraMatrix").mat()
    distCoeffs = p_file.getNode("distCoeffs").mat()
    #Cerrar Archivo
    p_file.release()

    return (cameraMatrix, distCoeffs)

def main_camera():
    #Menu de opciones
    parser = argparse.ArgumentParser(description="Basic marker detection")
    parser.add_argument('-ci', type=int, default=0,
    help="Camera id if input doesn’t come from video (-v)")
    parser.add_argument('-c', type=str, default="../camera/calibration/calibracion_camara.yml",
    help="Camera intrinsic parameters file (needed for camera pose estimation)")
    parser.add_argument('-l', type=float, default=0.1,
    help="Marker side length (in meters); needed for correct scale in camera pose")

    #recoge los escrito en la terminal, si no hay respuesta todo se setea al default del menu
    args = parser.parse_args()
    #parametros del .yml
    cameraMatrix, distCoeffs = extract_yml(args.c)
    #Activa la cámara web
    inputVideo = cv.VideoCapture(args.ci)
    #colección exacta de marcadores que debe busca
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    #Genera un paquete con los ajustes por defecto para localizar las esquinas y leer los códigos
    parametros = aruco.DetectorParameters()

    # Define las 4 esquinas del marcador 3D en el mundo real (Z=0). 
    # Multiplica un cuadrado básico por la mitad del tamaño físico para centrarlo en el origen (0,0).
    obj_points = np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=np.float32) * (args.l / 2.0)
    # Inicializa la búsqueda empaquetando el diccionario y las reglas de detección.
    detector = aruco.ArucoDetector(diccionario, parametros)

    while True:
        ret, image = inputVideo.read()
        if not ret:
            break

        #rectifica la imagen capturada con los parametros del .yml
        image_rect = cv.undistort(image, cameraMatrix, distCoeffs)
        
        # Busca los marcadores en la imagen rectificada. Devuelve sus coordenadas 2D (corners), 
        # sus identificadores (ids) y los posibles falsos positivos descartados (rejected).
        corners, ids, rejected = detector.detectMarkers(image_rect)

        if ids is not None:
            # Dibuja un contorno verde alrededor de cada marcador detectado y escribe su número de ID.
            aruco.drawDetectedMarkers(image_rect, corners, ids)
        
            # Recorre cada marcador encontrado individualmente para calcular su posición 3D.
            for i in range(len(ids)):
                        # solvePnP: Calcula la rotación (rvec) y la distancia/posición (tvec) del marcador.
            # Lo hace cruzando la forma 3D ideal (obj_points) con las esquinas 2D que ve la cámara (corners[i]).
                _, rvec, tvec = cv.solvePnP(obj_points, corners[i], cameraMatrix, distCoeffs)
                cv.drawFrameAxes(image_rect, cameraMatrix, distCoeffs, rvec, tvec, args.l)

        # Muestra imagen original y con detectando los Arucos
        cv.imshow("Imagen Original", image)
        cv.imshow("Deteccion ArUco", image_rect)

        # Salir con la tecla ESC
        if cv.waitKey(1) == 27: # ESC
            break

    inputVideo.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main_camera()