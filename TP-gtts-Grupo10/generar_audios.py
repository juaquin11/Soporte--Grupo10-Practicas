"""
Script opcional para pre-generar los archivos de audio MP3 de la Trivia
almacenándolos localmente en la carpeta 'audios/'.
"""

import os
import json
from gtts import gTTS

def generar_audios_locales():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audios_dir = os.path.join(base_dir, "audios")
    os.makedirs(audios_dir, exist_ok=True)

    # 1. Cargar preguntas
    ruta_json = os.path.join(base_dir, "preguntas.json")
    with open(ruta_json, 'r', encoding='utf-8') as f:
        preguntas = json.load(f)

    print("Generando audios MP3 en la carpeta 'audios/'...")

    # 2. Generar audio para cada pregunta
    for idx, q in enumerate(preguntas):
        filename = os.path.join(audios_dir, f"pregunta_{idx+1}.mp3")
        tts = gTTS(text=q["texto"], lang='es')
        tts.save(filename)
        print(f" Audio de Pregunta {idx+1} generado: {filename}")

    # 3. Generar audios de feedback
    tts_correcto = gTTS(text="¡Respuesta correcta!", lang='es')
    tts_correcto.save(os.path.join(audios_dir, "correcto.mp3"))

    tts_incorrecto = gTTS(text="Respuesta incorrecta.", lang='es')
    tts_incorrecto.save(os.path.join(audios_dir, "incorrecto.mp3"))

    print(" ¡Todos los audios fueron generados exitosamente!")

if __name__ == "__main__":
    generar_audios_locales()
