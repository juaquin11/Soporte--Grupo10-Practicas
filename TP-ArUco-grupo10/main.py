"""
TP: Sistema de Inspección y Realidad Aumentada 3D con Marcadores ArUco
Asignatura: Soporte / Visión por Computadora
Grupo: 10

Descripción:
Este script detecta marcadores ArUco en tiempo real mediante la cámara,
estima la pose 3D (posición y orientación), proyecta una Pirámide 3D
con ejes de coordenadas (X, Y, Z) y muestra telemetría de distancia en pantalla (HUD).
"""

import cv2
import numpy as np
from cv2 import aruco
import os
import time

# ==========================================
# CONFIGURACIÓN GENERAL Y PARÁMETROS
# ==========================================
MARKER_SIZE = 0.05   # Tamaño real del marcador en metros (5 cm)
PYRAMID_HEIGHT = 0.08 # Altura de la pirámide 3D en metros (8 cm)

# Matriz intrínseca de cámara estimada (Resolución 640x480)
CAMERA_MATRIX = np.array([
    [800.0, 0.0,   320.0],
    [0.0,   800.0, 240.0],
    [0.0,   0.0,   1.0]
], dtype=np.float32)

DIST_COEFFS = np.zeros((4, 1), dtype=np.float32) # Coeficientes de distorsión (cámara ideal)

# Puntos 3D del marcador (Top-Left, Top-Right, Bottom-Right, Bottom-Left)
MARKER_3D_POINTS = np.array([
    [-MARKER_SIZE / 2,  MARKER_SIZE / 2, 0.0],
    [ MARKER_SIZE / 2,  MARKER_SIZE / 2, 0.0],
    [ MARKER_SIZE / 2, -MARKER_SIZE / 2, 0.0],
    [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0.0]
], dtype=np.float32)

# Puntos 3D de la Pirámide (Base alineada + Ápice elevando hacia la cámara)
PYRAMID_3D_POINTS = np.array([
    [-MARKER_SIZE / 2,  MARKER_SIZE / 2, 0.0],              # 0: Top-Left
    [ MARKER_SIZE / 2,  MARKER_SIZE / 2, 0.0],              # 1: Top-Right
    [ MARKER_SIZE / 2, -MARKER_SIZE / 2, 0.0],              # 2: Bottom-Right
    [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0.0],              # 3: Bottom-Left
    [ 0.0,              0.0,            -PYRAMID_HEIGHT]    # 4: Ápice (Proyectado hacia la cámara)
], dtype=np.float32)

# Puntos 3D para los Ejes de Coordenadas
AXIS_3D_POINTS = np.array([
    [0.0,         0.0,         0.0],
    [MARKER_SIZE, 0.0,         0.0],          # Eje X (Rojo)
    [0.0,         MARKER_SIZE, 0.0],          # Eje Y (Verde)
    [0.0,         0.0,        -MARKER_SIZE]   # Eje Z (Azul - Hacia la cámara)
], dtype=np.float32)


def dibujar_ejes_3d(frame, rvec, tvec):
    """
    Proyecta y dibuja los ejes de coordenadas 3D (X: Rojo, Y: Verde, Z: Azul)
    sobre el origen del marcador ArUco.
    """
    img_pts, _ = cv2.projectPoints(AXIS_3D_POINTS, rvec, tvec, CAMERA_MATRIX, DIST_COEFFS)
    img_pts = np.int32(img_pts).reshape(-1, 2)
    origen = tuple(img_pts[0])

    # Eje X - Rojo
    cv2.line(frame, origen, tuple(img_pts[1]), (0, 0, 255), 3)
    # Eje Y - Verde
    cv2.line(frame, origen, tuple(img_pts[2]), (0, 255, 0), 3)
    # Eje Z - Azul
    cv2.line(frame, origen, tuple(img_pts[3]), (255, 0, 0), 3)


def dibujar_piramide_3d(frame, rvec, tvec):
    """
    Proyecta los puntos 3D de la pirámide a la imagen 2D y renderiza
    sus aristas y base.
    """
    img_pts, _ = cv2.projectPoints(PYRAMID_3D_POINTS, rvec, tvec, CAMERA_MATRIX, DIST_COEFFS)
    pts = np.int32(img_pts).reshape(-1, 2)

    base_pts = pts[:4]
    apice_pt = tuple(pts[4])

    # 1. Dibujar contorno de la base (Verde neón grueso)
    cv2.drawContours(frame, [base_pts], -1, (0, 255, 0), 3)

    # 2. Dibujar las 4 aristas que conectan la base con el ápice (Cian / Amarillo brillante)
    colores_aristas = [(255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
    for i in range(4):
        cv2.line(frame, tuple(base_pts[i]), apice_pt, colores_aristas[i], 3)

    # 3. Marcar el ápice con un círculo prominente (Rojo)
    cv2.circle(frame, apice_pt, 7, (0, 0, 255), -1)
    cv2.circle(frame, apice_pt, 9, (255, 255, 255), 2)


def dibujar_hud(frame, marcadores_detectados, info_telemetria):
    """
    Dibuja un panel overlay semi-transparente estilo HUD (Head-Up Display)
    con la información de telemetría y estado.
    """
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (340, 130), (20, 20, 20), -1)
    # Aplicar transparencia alpha
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.rectangle(frame, (10, 10), (340, 130), (0, 255, 255), 1)

    cv2.putText(frame, "INSPECCION ARUCO 3D - GRUPO 10", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    
    cv2.putText(frame, f"Marcadores en escena: {marcadores_detectados}", (20, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if marcadores_detectados > 0 else (0, 0, 255), 1, cv2.LINE_AA)

    if info_telemetria:
        marker_id, dist_cm, dist_m = info_telemetria
        cv2.putText(frame, f"ID Objetivo: {marker_id}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Distancia: {dist_cm:.1f} cm ({dist_m:.2f} m)", (20, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Esperando marcador...", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web.")
        return

    # Configuración del detector ArUco
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    print("=====================================================")
    print("  Sistema de Realidad Aumentada ArUco - Pirámide 3D  ")
    print("=====================================================")
    print("Controles:")
    print("  [Q] - Salir de la aplicación")
    print("  [S] - Capturar y guardar pantalla actual")
    print("=====================================================")

    captura_idx = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar fotograma de la cámara.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        num_detectados = len(ids) if ids is not None else 0
        telemetria_principal = None

        if ids is not None:
            # Dibujar bordes 2D por defecto de ArUco
            aruco.drawDetectedMarkers(frame, corners, ids)

            for i in range(num_detectados):
                img_points = corners[i][0]

                # Resolver Pose (solvePnP)
                success, rvec, tvec = cv2.solvePnP(
                    MARKER_3D_POINTS, img_points, CAMERA_MATRIX, DIST_COEFFS
                )

                if success:
                    # Calcular la distancia tridimensional euclidiana en metros
                    dist_m = float(np.linalg.norm(tvec))
                    dist_cm = dist_m * 100.0

                    marker_id = int(np.ravel(ids)[i])
                    if i == 0:
                        telemetria_principal = (marker_id, dist_cm, dist_m)

                    # 1. Dibujar pirámide 3D
                    dibujar_piramide_3d(frame, rvec, tvec)

                    # 2. Dibujar ejes 3D
                    dibujar_ejes_3d(frame, rvec, tvec)

                    # 3. Mostrar etiqueta con distancia flotando sobre el marcador
                    centro_2d = np.mean(img_points, axis=0).astype(int)
                    cv2.putText(frame, f"ID:{marker_id} ({dist_cm:.1f}cm)", 
                                (centro_2d[0] - 40, centro_2d[1] - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Dibujar panel HUD superior
        dibujar_hud(frame, num_detectados, telemetria_principal)

        # Mostrar ventana
        cv2.imshow("TP ArUco - Piramide 3D y Telemetria", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"captura_aruco_{captura_idx}.png"
            cv2.imwrite(filename, frame)
            print(f" Captura guardada como: {filename}")
            captura_idx += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
