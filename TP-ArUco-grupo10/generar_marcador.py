import cv2
from cv2 import aruco
import os

def generar_marcadores():
    # Directorio de salida
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Obtener el diccionario ArUco 6x6_250
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    
    # Generar marcadores con ID 0, 1 y 2
    for marker_id in [0, 1, 2]:
        # Generar imagen de 400x400 píxeles
        marker_img = aruco.generateImageMarker(aruco_dict, marker_id, 400)
        
        file_path = os.path.join(output_dir, f"marcador_id_{marker_id}.png")
        cv2.imwrite(file_path, marker_img)
        print(f"Marcador ArUco ID {marker_id} guardado en: {file_path}")

if __name__ == '__main__':
    generar_marcadores()
