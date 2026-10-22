import cv2

cv_file = cv2.FileStorage("calibracion_camara.yml", cv2.FILE_STORAGE_READ)
matriz_camara = cv_file.getNode("cameraMatrix").mat()
coeficientes_distorsion = cv_file.getNode("distCoeffs").mat()
cv_file.release()

imagen_original = cv2.imread("foto_tablero_2.jpg")

if imagen_original is None:
    print("Error: No se pudo cargar la imagen.")
    exit()

imagen_rectificada = cv2.undistort(imagen_original, matriz_camara, coeficientes_distorsion)

alto, ancho = imagen_original.shape[:2]
cv2.namedWindow("1. Imagen Original", cv2.WINDOW_NORMAL)
cv2.namedWindow("2. Imagen Rectificada", cv2.WINDOW_NORMAL)

cv2.resizeWindow("1. Imagen Original", ancho//2, alto//2)
cv2.resizeWindow("2. Imagen Rectificada", ancho//2, alto//2)

cv2.imshow("1. Imagen Original", imagen_original)
cv2.imshow("2. Imagen Rectificada", imagen_rectificada)

print("Imágenes en pantalla. Pulsa cualquier tecla sobre la ventana para cerrar.")
cv2.waitKey(0)
cv2.destroyAllWindows()