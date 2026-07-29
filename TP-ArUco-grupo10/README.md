# Trabajo Práctico: Sistema de Realidad Aumentada y Telemetría con Marcadores ArUco 3D

**Materia:** Soporte / Visión por Computadora  
**Grupo:** 10  

---

## 📌 1. Descripción del Proyecto

Este trabajo práctico amplía el uso de marcadores fiduciales **ArUco** e implementa un sistema interactivo de **Realidad Aumentada (RA)** y **Telemetría 3D** en tiempo real utilizando Python y OpenCV.

### Características Principales:
1. **Generación de Marcadores:** Script para generar e guardar marcadores ArUco imprimibles (Diccionario `6X6_250`).
2. **Estimación de Pose 3D (`solvePnP`):** Determinación precisa de los vectores de rotación (`rvec`) y traslación (`tvec`) del marcador respecto a la cámara.
3. **Renderizado de Pirámide 3D:** Proyección matemática de una pirámide tridimensional sobre el marcador.
4. **Ejes de Coordenadas 3D (XYZ):** Visualización del sistema de referencia tridimensional ($X$=Rojo, $Y$=Verde, $Z$=Azul).
5. **Telemetría y HUD en Tiempo Real:** Medición continua de la distancia euclidiana entre la cámara y el marcador en centímetros/metros con un panel de interfaz HUD.

---

## 📐 2. Fundamentos Teóricos

### A. Estimación de Pose ($Perspective-n-Point$)
Mediante la función `cv2.solvePnP()`, se relacionan las coordenadas 3D conocidas del marcador con sus 4 esquinas proyectadas en la imagen 2D:

$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \cdot [R | T] \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$

Donde:
- $K$ es la matriz intrínseca de la cámara.
- $[R | T]$ representa la rotación y traslación del objeto.
- $(X_w, Y_w, Z_w)$ son las coordenadas 3D del objeto.

### B. Medición de Distancia
La distancia euclidiana $D$ en el espacio 3D se calcula con la norma vectorial de $T = (t_x, t_y, t_z)$:

$$D = \sqrt{t_x^2 + t_y^2 + t_z^2}$$

---

## 🚀 3. Estructura de Archivos

```
TP-ArUco-Piramide3D/
├── generar_marcador.py   # Script para generar las imágenes de los marcadores ArUco
├── main.py               # Script principal con la detección, RA y telemetría
└── README.md             # Documentación del Trabajo Práctico
```

---

## 🛠️ 4. Instrucciones de Uso

### Requisitos Previos:
Tener instalado Python y la librería OpenCV con soporte para ArUco:
```bash
pip install opencv-python numpy
```

### Paso 1: Generar e imprimir los marcadores
Ejecutar el script generador para obtener las imágenes `marcador_id_0.png`, `marcador_id_1.png`, etc.:
```bash
python generar_marcador.py
```
*(Puedes mostrar la imagen `marcador_id_0.png` desde la pantalla del celular o imprimirla).*

### Paso 2: Ejecutar el sistema principal
```bash
python main.py
```

### Controles durante la ejecución:
- `Q`: Salir del programa.
- `S`: Guardar una captura de pantalla de la ventana actual.
