"""
==============================================================================
TRABAJO PRÁCTICO: ASISTENTE DE VOZ BIOMÉTRICO CON INTELIGENCIA ARTIFICIAL GEMINI
Asignatura: Soporte 2026 / Inteligencia Artificial
Grupo: 10

Descripción:
Asistente virtual conversacional con reconocimiento de voz (STT), verificación
biométrica del usuario (embeddings de voz), integración con Google Gemini LLM
y síntesis de voz hablada (TTS) en tiempo real.
==============================================================================
"""

import os
import sys
import io
import time
import signal
import tempfile
import threading
import numpy as np

# Codificación UTF-8 para consola de Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Cargar archivo .env local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except Exception:
    pass

# Fallback de lectura manual de .env
if "GEMINI_API_KEY" not in os.environ and os.path.exists(ENV_FILE):
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        os.environ["GEMINI_API_KEY"] = parts[1].strip(' "\'')
    except Exception:
        pass

# Importación segura de Pygame
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    HAS_PYGAME = True
except Exception as e:
    HAS_PYGAME = False
    print(f"[AVISO] Pygame Mixer no disponible: {e}")

# Importación segura de SpeechRecognition
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("[ERROR] Falta instalar SpeechRecognition: pip install SpeechRecognition")

# Importación segura de gTTS
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    from gTTS import gTTS
    HAS_GTTS = True

# Importación segura de Google Generative AI / GenAI / Requests REST API
HAS_GEMINI = False
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Importación de Resemblyzer para Biometría de Voz
HAS_RESEMBLYZER = False
try:
    # pyrefly: ignore [missing-import]
    from resemblyzer import VoiceEncoder, preprocess_wav
    HAS_RESEMBLYZER = True
except ImportError:
    pass


# PARÁMETROS DEL SISTEMA
WAKE_WORDS = ["guatemala", "jarvis", "hola", "gemini", "asistente"]
LANG_STT = "es-AR"
LANG_TTS = "es"
MODELOS_PREFERIDOS = ["gemma-4-31b-it", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
PROFILE_PATH = os.path.join(BASE_DIR, "voice_profile.npy")
SIMILARITY_THRESHOLD = 0.70
SYSTEM_PROMPT = (
    "Sos un asistente de voz inteligente, conciso y cordial. "
    "Respondé siempre en no más de 3 oraciones. Sé directo, claro y en español latinoamericano."
)


class AsistenteGeminiBiometrico:
    def __init__(self):
        print("\n" + "="*65)
        print("  ASISTENTE DE VOZ BIOMÉTRICO CON INTELIGENCIA ARTIFICIAL GEMINI")
        print("  Grupo: 10 - Soporte 2026")
        print("="*65)

        # 1. Configurar modelo de IA (Gemini / Gemma)
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.modelo_activo = None
        self.model = self.setup_gemini()

        # 2. Configurar reconocedor de voz
        self.recognizer = sr.Recognizer() if HAS_SR else None
        if self.recognizer:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.7

        # 3. Configurar Voice Encoder (Resemblyzer)
        self.encoder = None
        if HAS_RESEMBLYZER:
            try:
                print("Cargando modelo de embeddings biométricos de voz...")
                self.encoder = VoiceEncoder()
                print("[OK] Modelo biométrico cargado.")
            except Exception as e:
                print(f"[AVISO] Error al cargar VoiceEncoder: {e}")

        # 4. Cargar o crear perfil biométrico de voz
        self.perfil_voz = None
        if os.path.exists(PROFILE_PATH):
            try:
                self.perfil_voz = np.load(PROFILE_PATH)
                print(f"[OK] Perfil de voz biométrico cargado desde '{PROFILE_PATH}'.")
            except Exception as e:
                print(f"[AVISO] No se pudo leer {PROFILE_PATH}: {e}")

        print("[OK] Sistema iniciado correctamente.\n")

    def setup_gemini(self):
        """Inicializa la conexión con la API de Google Gemini / Gemma."""
        if not self.api_key:
            print("[AVISO] No se encontró la variable GEMINI_API_KEY en el archivo .env.")
            return None

        # Probar la clave con los modelos compatibles
        if HAS_REQUESTS:
            for m in MODELOS_PREFERIDOS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                try:
                    r = requests.post(url, json={"contents": [{"parts": [{"text": "test"}]}]}, timeout=5)
                    if r.status_code == 200:
                        self.modelo_activo = m
                        print(f"[OK] Conexión establecida con modelo de IA: {m}")
                        break
                except Exception:
                    pass

        if HAS_GEMINI and self.api_key:
            try:
                import google.generativeai as genai_lib
                genai_lib.configure(api_key=self.api_key)
                m_name = self.modelo_activo if self.modelo_activo else MODELOS_PREFERIDOS[0]
                model = genai_lib.GenerativeModel(m_name, system_instruction=SYSTEM_PROMPT)
                return model
            except Exception:
                pass

        if self.modelo_activo:
            return "REST_ACTIVE"

        print("[AVISO] No se pudo verificar modelo con cuota activa. Se usarán respuestas de soporte local.")
        return None

    def reproducir(self, texto):
        """Sintetiza texto a voz (gTTS) y lo reproduce."""
        print(f"\n🤖 [GEMINI]: {texto}")
        if not HAS_GTTS:
            return

        def _reproducir_thread():
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                tts = gTTS(text=texto, lang=LANG_TTS)
                tts.save(tmp_path)

                if HAS_PYGAME:
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                else:
                    os.system(f"start {tmp_path}")
            except Exception as e:
                print(f"[Aviso de audio]: {e}")
            finally:
                if HAS_PYGAME:
                    try:
                        pygame.mixer.music.unload()
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass

        threading.Thread(target=_reproducir_thread, daemon=True).start()

    def audio_a_numpy(self, audio_data):
        """Convierte datos de sr.AudioData a arreglo NumPy flotante para biometría."""
        wav_bytes = audio_data.get_wav_data(convert_rate=16000, convert_width=2)
        return np.frombuffer(wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    def verificar_biometria_voz(self, audio_data):
        """Verifica si la voz escuchada pertenece al usuario registrado."""
        if self.perfil_voz is None or self.encoder is None:
            # Si no hay perfil o encoder, permite el paso
            return True

        try:
            wav = preprocess_wav(self.audio_a_numpy(audio_data), source_sr=16000)
            embedding = self.encoder.embed_utterance(wav)
            similitud = np.dot(embedding, self.perfil_voz) / (
                np.linalg.norm(embedding) * np.linalg.norm(self.perfil_voz)
            )
            print(f"📊 [BIOMETRÍA] Similitud de voz: {similitud:.2f} (Umbral necesario: {SIMILARITY_THRESHOLD})")
            return similitud >= SIMILARITY_THRESHOLD
        except Exception as e:
            print(f"[Aviso Biometría]: {e}")
            return True

    def escuchar(self, source, timeout=10, phrase_limit=8):
        """Escucha y transcribir frase de voz."""
        if not self.recognizer:
            return None, None

        try:
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            texto = self.recognizer.recognize_google(audio, language=LANG_STT)
            return texto.strip().lower(), audio
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None, None
        except sr.RequestError as e:
            print(f"[Aviso STT]: Error de red en reconocimiento: {e}")
            return None, None

    def registrar_perfil_voz(self, source):
        """Registra e imparte el proceso de enrolamiento biométrico de voz del usuario."""
        self.reproducir("Iniciando registro de voz biométrico. ¿Cuál es tu nombre?")
        print("Registrando nuevo perfil de voz...")
        texto, _ = self.escuchar(source, timeout=8, phrase_limit=5)
        nombre = texto.split()[0].capitalize() if texto else "Usuario"

        self.reproducir(f"Hola {nombre}. Voy a grabar tres muestras de tu voz. Por favor habla cuando escuches la indicación.")

        embeddings = []
        for i in range(3):
            self.reproducir(f"Muestra {i+1} de 3. Habla ahora...")
            print(f"Grabando muestra {i+1}/3...")
            try:
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=5)
                if self.encoder:
                    wav = preprocess_wav(self.audio_a_numpy(audio), source_sr=16000)
                    embeddings.append(self.encoder.embed_utterance(wav))
            except Exception as e:
                print(f"[Aviso Muestra]: {e}")

        if embeddings:
            self.perfil_voz = np.mean(embeddings, axis=0)
            np.save(PROFILE_PATH, self.perfil_voz)
            self.reproducir(f"¡Excelente {nombre}! Tu perfil biométrico ha sido guardado. Ahora puedes hablarme.")
            print(f"[OK] Perfil guardado exitosamente en '{PROFILE_PATH}'.")

    def _limpiar_texto_respuesta(self, texto):
        """Filtra notas internas o formato markdown para dejar solo la frase limpia hablada."""
        lineas = [l.strip() for l in texto.split("\n") if l.strip() and not l.strip().startswith("*") and not l.strip().startswith("-")]
        if lineas:
            return lineas[-1]
        return texto.strip()

    def consultar_gemini(self, consulta_texto):
        """Envía la consulta a la IA Gemini / Gemma o genera respuesta local."""
        if self.model and hasattr(self.model, "generate_content"):
            try:
                respuesta = self.model.generate_content(consulta_texto).text
                return self._limpiar_texto_respuesta(respuesta)
            except Exception as e:
                print(f"[Error SDK Gemini]: {e}")

        if self.api_key and HAS_REQUESTS:
            modelo = self.modelo_activo if self.modelo_activo else "gemma-4-31b-it"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={self.api_key}"
            try:
                payload = {
                    "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nConsulta del usuario: {consulta_texto}"}]}]
                }
                r = requests.post(url, json=payload, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    respuesta = data['candidates'][0]['content']['parts'][0]['text']
                    return self._limpiar_texto_respuesta(respuesta)
                else:
                    print(f"[Aviso API {r.status_code}]: {r.json().get('error', {}).get('message')}")
            except Exception as e:
                print(f"[Error REST Gemini]: {e}")

        # Respuestas locales de respaldo
        if "hora" in consulta_texto:
            return f"Son las {time.strftime('%H:%M')}."
        elif "quien sos" in consulta_texto or "quién eres" in consulta_texto:
            return "Soy el Asistente de Voz Inteligente del Grupo 10."
        else:
            return f"Entendí tu consulta sobre: {consulta_texto}."

    def iniciar(self):
        if not HAS_SR:
            print("[ERROR CRÍTICO] Instale SpeechRecognition: pip install SpeechRecognition")
            return

        print("\n🎙️  Iniciando micrófono y calibrando ruido ambiente...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)

            # Verificar si se requiere registro biométrico
            if self.encoder and not os.path.exists(PROFILE_PATH):
                self.registrar_perfil_voz(source)
            else:
                self.reproducir("Asistente Gemini listo. Di una palabra de activación como 'Jarvis' o 'Hola' para hablar.")

            print("\n" + "-"*60)
            print(" [LISTO] Escuchando palabra de activación (Wake Word)...")
            print(" Palabras de activación: ", WAKE_WORDS)
            print("-"*60)

            while True:
                try:
                    texto_wake, _ = self.escuchar(source, timeout=12, phrase_limit=5)
                    if not texto_wake:
                        continue

                    print(f"👂 Escuché: '{texto_wake}'")

                    # Verificar si contiene palabra de activación
                    if not any(w in texto_wake for w in WAKE_WORDS):
                        continue

                    print("\n✨ ¡Asistente Activado!")
                    self.reproducir("Te escucho, ¿en qué puedo ayudarte?")

                    # Escuchar consulta principal
                    consulta, audio_consulta = self.escuchar(source, timeout=8, phrase_limit=12)

                    if not consulta:
                        self.reproducir("No logré escuchar tu consulta. Intenta de nuevo.")
                        continue

                    # Verificar biometría de voz
                    if audio_consulta and not self.verificar_biometria_voz(audio_consulta):
                        print("🚫 [BIOMETRÍA RECHAZADA] Voz no coincide con el usuario registrado.")
                        self.reproducir("Acceso no autorizado. Tu tono de voz no coincide con el usuario registrado.")
                        continue

                    print(f"🗣️  Usuario: '{consulta}'")

                    # Consultar Gemini IA
                    respuesta = self.consultar_gemini(consulta)
                    self.reproducir(respuesta)

                except KeyboardInterrupt:
                    print("\n¡Hasta luego!")
                    break
                except Exception as e:
                    print(f"[Error en bucle]: {e}")


if __name__ == "__main__":
    asistente = AsistenteGeminiBiometrico()
    asistente.iniciar()
