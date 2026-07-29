"""
==============================================================================
TRABAJO PRÁCTICO: ASISTENTE VIRTUAL DE VOZ Y AUTOMATIZACIÓN DE ESCRITORIO
Asignatura: Soporte 2026 / Automatización
Grupo: 10

Descripción:
Asistente virtual modular e interactivo que escucha comandos por micrófono,
transcribe el audio en español usando SpeechRecognition (Google STT), responde por
voz (pyttsx3 / gTTS) y ejecuta automatizaciones nativas en Windows (abrir navegador,
crear notas dictadas en el escritorio, buscar en YouTube/Google, abrir calculadora,
herramienta de recortes y dar la fecha/hora).
==============================================================================
"""

import os
import sys
import io
import time
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
import threading

# Configuración de codificación UTF-8 para consola de Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Importación segura de SpeechRecognition
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("[AVISO] La librería 'speech_recognition' no está instalada. Ejecute: pip install SpeechRecognition")

# Detección de motores de audio de captura (PyAudio / sounddevice)
HAS_PYAUDIO = False
HAS_SOUNDDEVICE = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    pass

try:
    import sounddevice as sd
    import numpy as np
    HAS_SOUNDDEVICE = True
except ImportError:
    pass

# Detección de sintetizador de voz offline (pyttsx3) y online (gTTS)
HAS_PYTTSX3 = False
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    pass


class AsistenteVozLocal:
    """
    Clase principal del Asistente Virtual de Voz para automatización de Windows.
    """

    def __init__(self, idioma="es-ES"):
        self.idioma = idioma
        self.ejecutando = True
        self.umbral_energia = 300.0

        print("\n" + "="*65)
        print("    ASISTENTE VIRTUAL DE VOZ Y AUTOMATIZACIÓN - GRUPO 10")
        print("="*65)

        # 1. Reconocedor de Voz
        self.recognizer = sr.Recognizer() if HAS_SR else None
        if self.recognizer:
            self.recognizer.pause_threshold = 0.7        # Pausa entre palabras (respuesta rápida)
            self.recognizer.energy_threshold = 250       # Umbral inicial muy sensible
            self.recognizer.dynamic_energy_threshold = True

        # 2. Sintetizador de Voz (pyttsx3)
        self.engine = None
        if HAS_PYTTSX3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 165)
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if "spanish" in voice.name.lower() or "es" in voice.id.lower() or "helena" in voice.name.lower() or "sabina" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f"[AVISO] No se pudo inicializar pyttsx3: {e}")

        print("[OK] Asistente inicializado correctamente.")

    def hablar(self, texto):
        """Muestra el texto en consola y lo pronuncia en voz alta."""
        print(f"\n🤖 [ASISTENTE]: {texto}")
        if self.engine:
            try:
                self.engine.say(texto)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[Aviso TTS]: {e}")

    def calibrar_ruido_ambiental(self, source=None):
        """Calibra el umbral de ruido de fondo."""
        print("\n[INFO] Calibrando silencio ambiental (1 segundo)...")
        if HAS_PYAUDIO and source is not None and self.recognizer:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                # Limitar umbral a rango óptimo para voz humana
                self.recognizer.energy_threshold = min(600.0, max(150.0, float(self.recognizer.energy_threshold)))
                print(f"[OK] Calibración completada. Umbral ajustado a: {self.recognizer.energy_threshold:.1f}")
                return
            except Exception:
                pass

        print("[INFO] Usando umbral estándar súper sensible: 250.0")

    def capturar_audio(self, source=None, duracion_max=8):
        """Graba audio desde el micrófono del sistema."""
        if HAS_PYAUDIO and source is not None and self.recognizer:
            try:
                print("\n🎙️  [ESCUCHANDO] Habla ahora... (ej: 'qué hora es', 'abrir calculadora', 'escribe una nota')")
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=duracion_max)
                print("⚡ [AUDIO DETECTADO] Procesando comando de voz...")
                return audio
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                print(f"[Aviso de audio]: {e}")

        if HAS_SOUNDDEVICE and self.recognizer:
            try:
                print("\n🎙️  Escuchando... (Hable ahora)")
                sample_rate = 16000
                chunk_dur = 0.5
                chunk_samples = int(sample_rate * chunk_dur)
                total_chunks = int(duracion_max / chunk_dur)

                frames = []
                hablando = False
                silencio_cont = 0

                for _ in range(total_chunks):
                    data = sd.rec(chunk_samples, samplerate=sample_rate, channels=1, dtype='int16')
                    sd.wait()
                    rms = np.sqrt(np.mean(data.astype(np.float32)**2)) if len(data) > 0 else 0

                    if rms > self.umbral_energia:
                        hablando = True
                        silencio_cont = 0
                        frames.append(data.tobytes())
                    elif hablando:
                        silencio_cont += 1
                        frames.append(data.tobytes())
                        if silencio_cont >= 3:
                            break

                if not frames:
                    return None

                return sr.AudioData(b''.join(frames), sample_rate, 2)

            except Exception as e:
                print(f"[Aviso sounddevice]: {e}")
                return None

        print("[ERROR] No se detectó un dispositivo de micrófono compatible.")
        return None

    def transcribir_audio(self, audio_data):
        """Convierte los datos de audio grabado a texto con Google Speech Recognition."""
        if audio_data is None or not self.recognizer:
            return ""

        try:
            print("⚡ Procesando voz con Google STT...")
            texto = self.recognizer.recognize_google(audio_data, language=self.idioma)
            return texto.strip().lower()

        except sr.UnknownValueError:
            print("[STT] No se comprendió el audio.")
            return ""
        except sr.RequestError as e:
            print(f"[ERROR STT] Error de conexión: {e}")
            return ""
        except Exception as e:
            print(f"[ERROR] {e}")
            return ""

    # ==========================================
    # COMANDOS DE AUTOMATIZACIÓN
    # ==========================================

    def comando_navegador(self):
        self.hablar("Abriendo el navegador predeterminado...")
        webbrowser.open("https://www.google.com")

    def comando_nota(self, source):
        self.hablar("Modo dictado activado. Diga el contenido de su nota...")
        audio = self.capturar_audio(source, duracion_max=15)
        dictado = self.transcribir_audio(audio)

        if not dictado:
            self.hablar("No se capturó ningún texto. Dictado cancelado.")
            return

        print(f"\n📝 Dictado recibido: \"{dictado}\"")

        try:
            escritorio = Path.home() / "Desktop"
            if not escritorio.exists():
                escritorio = Path.home()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_nota = escritorio / f"Nota_Voz_{timestamp}.txt"

            with open(ruta_nota, "w", encoding="utf-8") as f:
                f.write("=== NOTA DE VOZ AUTOMÁTICA ===\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write(f"Contenido:\n{dictado}\n")

            self.hablar("Nota guardada en el Escritorio y lista para revisar.")
            os.startfile(ruta_nota)

        except Exception as e:
            print(f"[ERROR]: {e}")
            self.hablar("Ocurrió un error al guardar la nota.")

    def comando_hora(self):
        ahora = datetime.now()
        mensaje = f"Hoy es {ahora.strftime('%d/%m/%Y')} y son las {ahora.strftime('%H:%M')}."
        self.hablar(mensaje)

    def comando_calculadora(self):
        self.hablar("Abriendo la calculadora de Windows...")
        try:
            subprocess.Popen("calc.exe")
        except Exception as e:
            print(f"[ERROR]: {e}")

    def comando_youtube(self, texto):
        busqueda = texto.replace("buscar en youtube", "").replace("youtube", "").strip()
        if busqueda:
            url = f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
            self.hablar(f"Buscando '{busqueda}' en YouTube...")
        else:
            url = "https://www.youtube.com"
            self.hablar("Abriendo YouTube...")
        webbrowser.open(url)

    def comando_google(self, texto):
        busqueda = texto.replace("buscar en google", "").replace("busca en google", "").strip()
        if busqueda:
            url = f"https://www.google.com/search?q={busqueda.replace(' ', '+')}"
            self.hablar(f"Buscando '{busqueda}' en Google...")
            webbrowser.open(url)
        else:
            self.comando_navegador()

    def comando_captura(self):
        self.hablar("Abriendo la herramienta de capturas...")
        os.system("start ms-screenclip:")

    def comando_adios(self):
        self.hablar("Hasta luego. Cerrando el asistente de voz.")
        self.ejecutando = False

    def procesar_comando(self, texto, source):
        if not texto:
            return

        print(f"\n🗣️  [COMANDO RECONOCIDO]: \"{texto}\"")

        if "abrir navegador" in texto or "abre el navegador" in texto:
            self.comando_navegador()
        elif any(p in texto for p in ["escribe una nota", "crear nota", "nueva nota", "dictar nota"]):
            self.comando_nota(source)
        elif any(p in texto for p in ["qué hora es", "que hora es", "la hora"]):
            self.comando_hora()
        elif any(p in texto for p in ["calculadora", "abrir calculadora"]):
            self.comando_calculadora()
        elif "youtube" in texto:
            self.comando_youtube(texto)
        elif "google" in texto:
            self.comando_google(texto)
        elif "captura" in texto:
            self.comando_captura()
        elif any(p in texto for p in ["adiós", "adios", "terminar", "cerrar asistente"]):
            self.comando_adios()
        else:
            print("❓ Comando no reconocido.")
            print("   Comandos disponibles: 'abrir navegador', 'escribe una nota', 'qué hora es',")
            print("                         'calculadora', 'buscar en youtube ...', 'captura', 'adiós'")

    def iniciar(self):
        if not HAS_SR:
            print("[ERROR CRÍTICO] Se requiere instarlar SpeechRecognition: pip install SpeechRecognition")
            return

        microfono_sr = None
        if HAS_PYAUDIO:
            try:
                microfono_sr = sr.Microphone()
                print("[AUDIO] Micrófono PyAudio instanciado.")
            except Exception:
                microfono_sr = None

        try:
            if microfono_sr:
                with microfono_sr as source:
                    self.calibrar_ruido_ambiental(source)
                    self.hablar("Asistente de voz iniciado y listo.")
                    while self.ejecutando:
                        audio = self.capturar_audio(source)
                        if audio:
                            texto = self.transcribir_audio(audio)
                            self.procesar_comando(texto, source)
                        time.sleep(0.2)
            else:
                self.calibrar_ruido_ambiental(None)
                self.hablar("Asistente de voz iniciado y listo.")
                while self.ejecutando:
                    audio = self.capturar_audio(None)
                    if audio:
                        texto = self.transcribir_audio(audio)
                        self.procesar_comando(texto, None)
                    time.sleep(0.2)

        except KeyboardInterrupt:
            print("\n[STOP] Asistente detenido por el usuario.")
        except Exception as e:
            print(f"\n[ERROR]: {e}")
        finally:
            print("[FIN] Sesión finalizada.")


if __name__ == "__main__":
    asistente = AsistenteVozLocal(idioma="es-ES")
    asistente.iniciar()
