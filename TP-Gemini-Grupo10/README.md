# Trabajo Práctico: Asistente de Voz Biométrico Inteligente con Google Gemini

**Materia:** Soporte / Inteligencia Artificial  
**Grupo:** 10  

---

## 📌 1. Descripción del Proyecto

Este trabajo práctico desarrolla un **Asistente de Voz Inteligente Avanzado** que combina:
1. **Reconocimiento de Voz (STT):** Captura continua del habla en español usando `SpeechRecognition`.
2. **Verificación Biométrica por Voz:** Utiliza **embeddings de voz** tridimensionales (modelo d-vector de `resemblyzer`) para verificar si la persona que habla es el usuario registrado autorizando las consultas.
3. **Generación Inteligente con LLM (Google Gemini):** Integración con la API de **Google Gemini** (`gemini-flash-latest` / `gemini-2.0-flash`) para responder preguntas complejas de manera concisa y natural.
4. **Síntesis de Voz (TTS):** Respuesta hablada en tiempo real mediante `gTTS` y reproducción asíncrona por altavoz.

---

## 📐 2. Arquitectura del Pipeline

```
                +----------------------------+
                |    Captura de Audio (STT)  |
                +--------------+-------------+
                               |
                               v
                +--------------+-------------+
                |  Detección de Wake Word    |
                | ("Jarvis", "Hola", etc.)   |
                +--------------+-------------+
                               |
                               v
                +--------------+-------------+
                |  Verificación Biométrica   |
                | (Similitud Coseno > 0.70)  |
                +--------------+-------------+
                               | (Voz Autorizada)
                               v
                +--------------+-------------+
                |   Google Gemini LLM API    |
                +--------------+-------------+
                               |
                               v
                +--------------+-------------+
                |  Síntesis de Voz (gTTS)    |
                +----------------------------+
```

---

## 🚀 3. Estructura de Archivos

```
TP-Gemini-Asistente-Biometrico-Grupo10/
├── asistente_gemini.py   # Script principal con biometría, STT, Gemini y TTS
├── .env.example           # Plantilla para la variable GEMINI_API_KEY
└── README.md              # Documentación técnica del Trabajo Práctico
```

---

## 🛠️ 4. Requisitos e Instalación

### Librerías Requeridas:
```bash
pip install google-generativeai SpeechRecognition gtts pygame python-dotenv numpy
```
*(Opcional para biometría de voz avanzada: `pip install resemblyzer`)*.

### Configuración de la Clave API de Gemini:
1. Crea un archivo `.env` en la carpeta del proyecto basándote en `.env.example`.
2. Añade tu API Key obtenida de [Google AI Studio](https://aistudio.google.com/):
   ```env
   GEMINI_API_KEY=tu_clave_aqui
   ```

### Ejecución:
```bash
python asistente_gemini.py
```
