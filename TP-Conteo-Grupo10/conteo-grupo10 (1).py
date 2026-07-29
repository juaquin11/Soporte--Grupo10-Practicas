import cv2
import numpy as np
import math

class RastreadorEuclidiano:
    def __init__(self):
        self.centro_puntos = {} 
        self.id_count = 0

    def actualizar(self, cajas):
        cajas_ids = []
        for caja in cajas:
            x, y, w, h = caja
            cx = x + w // 2
            cy = y + h // 2
            
            objeto_detectado = False
            for id_obj, pt in self.centro_puntos.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                
                # Si la distancia es menor a un umbral, 
                # consideramos que es el mismo objeto
                if dist < 60:
                    self.centro_puntos[id_obj] = (cx, cy)
                    cajas_ids.append([x, y, w, h, id_obj])
                    objeto_detectado = True
                    break
            
            # Si el objeto no coincidió con ninguno previo, es nuevo
            if not objeto_detectado:
                self.centro_puntos[self.id_count] = (cx, cy)
                cajas_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
                
        # Actualizar el diccionario para limpiar IDs que ya no están en pantalla
        nuevos_centros = {}
        for caja_id in cajas_ids:
            _, _, _, _, id_obj = caja_id
            nuevos_centros[id_obj] = self.centro_puntos[id_obj]
            
        self.centro_puntos = nuevos_centros.copy()
        return cajas_ids

def main():
    import os
    video_path = '000.mp4'
    if os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        print("Cargando video: 000.mp4")
    else:
        cap = cv2.VideoCapture(0)
        print("No se encontró 000.mp4. Iniciando cámara web en tiempo real...")
    
    if not cap.isOpened():
        print("Error al abrir la fuente de video o cámara.")
        return

    # Obtener resolución del video para dibujar la barrera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Posición Y de la línea virtual
    line_y = height // 2

    #Inicializar Sustractor de fondo y Rastreador
    subtractor = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=30, detectShadows=True)
    rastreador = RastreadorEuclidiano()

    # Variables para conteo
    conteo = 0
    objetos_contados = set()
    posiciones_previas = {} 

    # Kernel para operaciones morfológicas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    while True:
        ret, frame = cap.read()
        if not ret:
            break # Fin del video
            
        #Máscara para detectar movimiento
        mask = subtractor.apply(frame)
        
        # Eliminar sombras grises dejadas por MOG2
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY) 
        
        # Eliminar ruido exterior
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel) 
        # Rellenar huecos interiores del objeto en movimiento
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) 
        
        #Buscar contornos en la máscara limpia
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cajas_detectadas = []
        for c in contornos:
            area = cv2.contourArea(c)
            # Umbral de área bajo (150 px) para capturar cualquier tipo de objeto en movimiento
            if area > 150: 
                x, y, w, h = cv2.boundingRect(c)
                cajas_detectadas.append([x, y, w, h])
                
        # Rastrear objetos e identificarlos a través del tiempo
        cajas_rastreadas = rastreador.actualizar(cajas_detectadas)
        
        # Dibujar línea de la barrera virtual
        cv2.line(frame, (0, line_y), (width, line_y), (255, 127, 0), 2)
        
        for caja in cajas_rastreadas:
            x, y, w, h, id_obj = caja
            cx = x + w // 2 # Centro X
            cy = y + h // 2 # Centro Y
            
            # Dibujar rectángulo y punto central
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"ID: {id_obj}", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
            
            #Lógica de conteo
            if id_obj in posiciones_previas:
                y_previa = posiciones_previas[id_obj]
                
                # Si el centroide cruzó la barrera en cualquier dirección (arriba a abajo o viceversa)
                if (y_previa <= line_y <= cy) or (cy <= line_y <= y_previa):
                    if id_obj not in objetos_contados:
                        objetos_contados.add(id_obj)
                        
            # Guardar la posición actual para el siguiente frame
            posiciones_previas[id_obj] = cy


        conteo_total = len(objetos_contados)
        cv2.putText(frame, f"Conteo: {conteo_total}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Redimensionar la imagen
        escala = 0.6
        frame_redimensionado = cv2.resize(frame, (0, 0), fx=escala, fy=escala)
        mask_redimensionada = cv2.resize(mask, (0, 0), fx=escala, fy=escala)
        

        cv2.imshow("Video Original (Rastreo)", frame_redimensionado)
        cv2.imshow("Mascara de Movimiento", mask_redimensionada)
        

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

 
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()