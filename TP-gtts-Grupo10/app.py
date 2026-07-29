"""
TP: Quiz Interactivo de Soporte Técnico con Síntesis de Voz (TTS)
Asignatura: Soporte 2026
Grupo: 10

Descripción:
Aplicación multimedia e interactiva desarrollada en Python y Tkinter.
Carga preguntas de Soporte Técnico desde un archivo JSON, lee las preguntas
en voz alta utilizando síntesis de voz (gTTS + Pygame Mixer) en hilos asíncronos
y ofrece una interfaz gráfica moderna con métricas y retroalimentación en tiempo real.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import json
import random
import time
# Importación segura de gTTS y Pygame
try:
    try:
        from gtts import gTTS
    except ImportError:
        from gTTS import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    print("Aviso: gTTS no está instalado en este entorno Python. Modo audio desactivado.")

try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except Exception as e:
    HAS_PYGAME = False
    print(f"Aviso: Pygame mixer no disponible: {e}")

# ==========================================
# PALETA DE COLORES Y ESTILOS DE LA INTERFAZ
# ==========================================
COLOR_BG = "#1e1e2e"          # Fondo oscuro elegante
COLOR_CARD = "#2b2b3b"        # Fondo de la tarjeta central
COLOR_TEXT = "#cdd6f4"        # Texto claro
COLOR_ACCENT = "#89b4fa"      # Azul acento
COLOR_SUCCESS = "#a6e3a1"     # Verde correcto
COLOR_ERROR = "#f38ba8"       # Rojo incorrecto
COLOR_BTN = "#313244"         # Fondo botones opción
COLOR_BTN_HOVER = "#45475a"   # Fondo al pasar el cursor


class QuizVozApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Interactivo de Soporte Técnico con Voz - Grupo 10")
        self.root.geometry("680x520")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        # Inicializar el mezclador de audio de Pygame
        pygame.mixer.init()

        # Cargar base de datos de preguntas
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(base_dir, "preguntas.json")
        self.preguntas = self.cargar_preguntas(ruta_json)

        # Variables de estado
        self.indice_actual = 0
        self.puntaje = 0
        self.bloqueado = False
        self.hilo_audio_actual = None

        # Construir Interfaz Gráfica
        self.crear_interfaz()

        # Iniciar Trivia si hay preguntas
        if self.preguntas:
            # Aleatorizar el orden de las preguntas al iniciar
            random.shuffle(self.preguntas)
            self.cargar_pregunta()
        else:
            self.lbl_pregunta.config(text="Error: No se pudo cargar el archivo preguntas.json")

    def cargar_preguntas(self, ruta_archivo):
        """Carga y valida el archivo JSON de preguntas."""
        if not os.path.exists(ruta_archivo):
            print(f"Error: Archivo no encontrado en {ruta_archivo}")
            return []
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer JSON: {e}")
            return []

    def crear_interfaz(self):
        """Crea los componentes visuales de Tkinter."""
        # 1. Encabezado / Título
        self.frame_top = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_top.pack(fill="x", padx=20, pady=15)

        self.lbl_titulo = tk.Label(
            self.frame_top, 
            text="TRIVIA DE SOPORTE TÉCNICO", 
            font=("Segoe UI", 16, "bold"), 
            bg=COLOR_BG, 
            fg=COLOR_ACCENT
        )
        self.lbl_titulo.pack(side="left")

        self.lbl_puntaje = tk.Label(
            self.frame_top, 
            text="Puntaje: 0", 
            font=("Segoe UI", 12, "bold"), 
            bg=COLOR_BG, 
            fg=COLOR_SUCCESS
        )
        self.lbl_puntaje.pack(side="right")

        # 2. Barra de Progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=25, pady=5)

        # 3. Tarjeta Central (Pregunta + Voz)
        self.card_frame = tk.Frame(self.root, bg=COLOR_CARD, bd=1, relief="solid")
        self.card_frame.pack(fill="both", expand=True, padx=25, pady=15)

        self.lbl_contador = tk.Label(
            self.card_frame, 
            text="Pregunta 1 de 6", 
            font=("Segoe UI", 10, "italic"), 
            bg=COLOR_CARD, 
            fg="#9399b2"
        )
        self.lbl_contador.pack(anchor="w", padx=15, pady=8)

        self.lbl_pregunta = tk.Label(
            self.card_frame, 
            text="", 
            font=("Segoe UI", 13, "bold"), 
            bg=COLOR_CARD, 
            fg=COLOR_TEXT, 
            wraplength=580, 
            justify="center"
        )
        self.lbl_pregunta.pack(pady=10, padx=15)

        # Botón para reproducir de nuevo la voz
        self.btn_reproducir_voz = tk.Button(
            self.card_frame, 
            text="🔊 Repetir Voz", 
            font=("Segoe UI", 9, "bold"), 
            bg="#45475a", 
            fg=COLOR_TEXT, 
            activebackground=COLOR_ACCENT, 
            activeforeground="#000000",
            relief="flat", 
            cursor="hand2", 
            command=self.repetir_voz
        )
        self.btn_reproducir_voz.pack(pady=5)

        # 4. Botones de Opciones
        self.frame_opciones = tk.Frame(self.card_frame, bg=COLOR_CARD)
        self.frame_opciones.pack(pady=10, fill="x", padx=15)

        self.botones_opciones = []
        for i in range(3):
            btn = tk.Button(
                self.frame_opciones, 
                text="", 
                font=("Segoe UI", 11), 
                bg=COLOR_BTN, 
                fg=COLOR_TEXT, 
                activebackground=COLOR_ACCENT, 
                activeforeground="#11111b", 
                relief="flat", 
                height=2, 
                cursor="hand2", 
                command=lambda idx=i: self.verificar_respuesta(idx)
            )
            btn.pack(fill="x", pady=5)
            # Efecto Hover al pasar el mouse
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b))
            btn.bind("<Leave>", lambda e, b=btn: self._on_leave(b))
            self.botones_opciones.append(btn)

        # 5. Label de Retroalimentación / Explicación
        self.lbl_feedback = tk.Label(
            self.card_frame, 
            text="", 
            font=("Segoe UI", 10, "bold"), 
            bg=COLOR_CARD, 
            fg=COLOR_TEXT, 
            wraplength=580, 
            justify="center"
        )
        self.lbl_feedback.pack(pady=10)

    def _on_hover(self, btn):
        if btn["state"] != "disabled":
            btn.configure(bg=COLOR_BTN_HOVER)

    def _on_leave(self, btn):
        if btn["state"] != "disabled":
            btn.configure(bg=COLOR_BTN)

    def hablar(self, texto):
        """Ejecuta la síntesis de voz (gTTS) en un hilo secundario sin congelar la GUI."""
        if not (HAS_GTTS and HAS_PYGAME):
            return

        def _run_tts():
            # Detener y descargar cualquier reproducción anterior
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass

            archivo_audio = f"temp_tts_{threading.get_ident()}.mp3"
            try:
                tts = gTTS(text=texto, lang='es')
                tts.save(archivo_audio)
                pygame.mixer.music.load(archivo_audio)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            except Exception as e:
                print(f"Aviso de audio (reproducción): {e}")
            finally:
                try:
                    pygame.mixer.music.unload()
                    if os.path.exists(archivo_audio):
                        os.remove(archivo_audio)
                except Exception:
                    pass

        threading.Thread(target=_run_tts, daemon=True).start()

    def repetir_voz(self):
        """Vuelve a leer el texto de la pregunta actual."""
        if self.indice_actual < len(self.preguntas):
            texto = self.preguntas[self.indice_actual]["texto"]
            self.hablar(texto)

    def cargar_pregunta(self):
        """Carga la pregunta actual en los componentes de la GUI."""
        self.bloqueado = False
        total = len(self.preguntas)
        
        if self.indice_actual < total:
            q = self.preguntas[self.indice_actual]
            
            # Actualizar barra e indicadores
            porcentaje = (self.indice_actual / total) * 100
            self.progress_var.set(porcentaje)
            self.lbl_contador.config(text=f"Pregunta {self.indice_actual + 1} de {total}")
            self.lbl_pregunta.config(text=q["texto"])
            self.lbl_feedback.config(text="")
            self.lbl_puntaje.config(text=f"Puntaje: {self.puntaje}")

            # Cargar botones de opciones
            for i, btn in enumerate(self.botones_opciones):
                btn.config(
                    text=f"{chr(65+i)})  {q['opciones'][i]}", 
                    state="normal", 
                    bg=COLOR_BTN, 
                    fg=COLOR_TEXT
                )

            # Leer la pregunta mediante sintetizador de voz
            self.hablar(q["texto"])
        else:
            self.mostrar_pantalla_final()

    def verificar_respuesta(self, idx_seleccionado):
        """Verifica si la respuesta fue correcta y brinda retroalimentación."""
        if self.bloqueado:
            return
        self.bloqueado = True

        # Deshabilitar botones de opciones
        for btn in self.botones_opciones:
            btn.config(state="disabled")

        q = self.preguntas[self.indice_actual]
        correcta = q["correcta"]
        explicacion = q.get("explicacion", "")

        if idx_seleccionado == correcta:
            self.puntaje += 1
            self.lbl_puntaje.config(text=f"Puntaje: {self.puntaje}")
            self.botones_opciones[idx_seleccionado].config(bg=COLOR_SUCCESS, fg="#11111b")
            self.lbl_feedback.config(text=f"¡CORRECTO! {explicacion}", fg=COLOR_SUCCESS)
            self.hablar(f"¡Correcto! {explicacion}")
        else:
            self.botones_opciones[idx_seleccionado].config(bg=COLOR_ERROR, fg="#11111b")
            self.botones_opciones[correcta].config(bg=COLOR_SUCCESS, fg="#11111b")
            self.lbl_feedback.config(text=f"INCORRECTO. {explicacion}", fg=COLOR_ERROR)
            self.hablar(f"Incorrecto. {explicacion}")

        # Pasar a la siguiente pregunta tras 3 segundos
        self.root.after(3200, self.siguiente_pregunta)

    def siguiente_pregunta(self):
        self.indice_actual += 1
        self.cargar_pregunta()

    def mostrar_pantalla_final(self):
        """Muestra los resultados finales de la trivia."""
        total = len(self.preguntas)
        porcentaje = (self.puntaje / total) * 100
        self.progress_var.set(100)

        # Ocultar opciones
        self.frame_opciones.pack_forget()
        self.btn_reproducir_voz.pack_forget()
        self.lbl_contador.config(text="¡COMPLETADO!")

        # Mensaje según el puntaje
        if porcentaje == 100:
            calificacion = "¡Excelente! Demostraste un dominio total de Soporte Técnico."
        elif porcentaje >= 60:
            calificacion = "¡Muy buen trabajo! Tienes muy buenos conocimientos generales."
        else:
            calificacion = "Buen intento. Te recomendamos repasar los conceptos de Hardware y Sistemas."

        mensaje_final = f"¡Juego Terminado!\n\nPuntaje Final: {self.puntaje} / {total} ({porcentaje:.0f}%)\n\n{calificacion}"
        self.lbl_pregunta.config(text=mensaje_final, fg=COLOR_ACCENT)
        self.lbl_feedback.config(text="")

        # Botón para Reiniciar Juego
        self.btn_reiniciar = tk.Button(
            self.card_frame, 
            text="🔄 Volver a Jugar", 
            font=("Segoe UI", 12, "bold"), 
            bg=COLOR_ACCENT, 
            fg="#11111b", 
            relief="flat", 
            cursor="hand2", 
            command=self.reiniciar_juego
        )
        self.btn_reiniciar.pack(pady=20)

        self.hablar(f"Juego terminado. Lograste {self.puntaje} respuestas correctas de {total}. {calificacion}")

    def reiniciar_juego(self):
        """Restablece el estado del juego para volver a jugar."""
        self.btn_reiniciar.destroy()
        self.btn_reproducir_voz.pack(pady=5)
        self.frame_opciones.pack(pady=10, fill="x", padx=15)
        
        self.indice_actual = 0
        self.puntaje = 0
        random.shuffle(self.preguntas)
        self.cargar_pregunta()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizVozApp(root)
    root.mainloop()
