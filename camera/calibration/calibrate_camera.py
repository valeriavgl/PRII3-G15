import numpy as np
import cv2
import glob
from pathlib import Path  

# --- CONFIGURACION ---
PATTERN_SIZE = (13, 9) 
SQUARE_SIZE = 30.0  

# Rutas y archivo de salida
BASE_DIR = Path(__file__).resolve().parents[2]
IMAGES_DIR = BASE_DIR / "imagenes_sprint2"
OUTPUT_FILE = BASE_DIR / "camera" / "calibration" / "calibracion_camara.yml"

def main():
    objp = np.zeros((PATTERN_SIZE[0] * PATTERN_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:PATTERN_SIZE[0], 0:PATTERN_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    object_points = []  
    image_points = []   

    # Buscar todas las imag
    image_paths = list(IMAGES_DIR.glob("*.jpg"))
    print(f"Fotografias encontradas en '{IMAGES_DIR}': {len(image_paths)}")

    if len(image_paths) == 0:
        print("[ERROR] No se encontraron imagenes. Revisa la ruta.")
        return

    image_size = None
    accepted = 0

    for image_path in image_paths:
        img = cv2.imread(str(image_path))
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if image_size is None:
            image_size = gray.shape[::-1] # (ancho, alto)

        # Buscar las esquinas del tablero de ajedrez
        ret, corners = cv2.findChessboardCorners(
            gray, 
            PATTERN_SIZE, 
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK
        )

        if ret:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            object_points.append(objp)
            image_points.append(refined_corners)
            accepted += 1
            print(f"[OK] {image_path.name}: esquinas detectadas correctamente")
        else:
            print(f"[NO DETECTADO] {image_path.name}: no se pudo encontrar el tablero")

    if accepted < 3:
        print("[ERROR] Muy pocas imágenes válidas para calibrar. Revisa las fotos y el PATTERN_SIZE.")
        return

    print(f"\nCalculando parametros de calibracion con {accepted} imagenes validas...")

    # Calcular la calibracion
    rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points, 
        image_points, 
        image_size, 
        None, 
        None
    )

    #  Guardar los resultados en el archivo YAML
    fs = cv2.FileStorage(str(OUTPUT_FILE), cv2.FILE_STORAGE_WRITE)
    if not fs.isOpened():
        print(f"[ERROR] No se pudo crear o abrir el archivo {OUTPUT_FILE}")
        return

    fs.write("cameraMatrix", camera_matrix)
    fs.write("distCoeffs", dist_coeffs)
    fs.write("image_width", image_size[0])
    fs.write("image_height", image_size[1])
    fs.write("rms_reprojection_error", float(rms))
    fs.release()

    # Mostrar resultados en consola
    print("\n--- RESULTADO DE CALIBRACION ---")
    print(f"Imagenes validas: {accepted}/{len(image_paths)}")
    print(f"Resolucion de imagen: {image_size[0]} x {image_size[1]}")
    print("\nMatriz de camara (cameraMatrix):")
    print(camera_matrix)
    print("\nCoeficientes de distorsion (distCoeffs):")
    print(dist_coeffs)
    print(f"\nError RMS de reproyeccion: {rms:.4f}")
    print(f"[EXITO] Archivo de calibracion guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()