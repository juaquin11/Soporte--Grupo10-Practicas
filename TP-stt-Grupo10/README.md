# Trabajo Práctico: Asistente Virtual de Voz y Automatización de Escritorio

**Materia:** Soporte 2026 / Automatización  
**Grupo:** 10  

---

## 📌 1. Descripción del Proyecto

Este trabajo práctico desarrolla un **Asistente Virtual de Voz en tiempo real** para la automatización de tareas comunes en el sistema operativo **Windows**. 

El sistema utiliza **SpeechRecognition (Google Speech-to-Text)** para procesar dictados por micrófono en español, un motor de **Síntesis de Voz (pyttsx3 / gTTS)** para responder por altavoz, y ejecutores nativos de comandos de Windows para controlar herramientas del sistema.

### Funcionalidades y Comandos Disponibles:
- 🌐 **"abrir navegador"**: Abre el navegador predeterminado en Google.
- 📝 **"escribe una nota"**: Activa el modo dictado por voz, graba la nota del usuario, guarda un archivo `.txt` fechado en el **Escritorio de Windows** y lo abre automáticamente.
- ⏰ **"qué hora es"**: Informa la fecha y hora actual por voz.
- 🧮 **"abrir calculadora"**: Inicia la Calculadora nativa del sistema (`calc.exe`).
- 🎬 **"buscar en youtube [tema]"**: Busca videos en YouTube según la solicitud de voz.
- 🔍 **"buscar en google [tema]"**: Realiza búsquedas directas en el navegador.
- ✂️ **"captura"**: Abre la Herramienta de Recortes de Windows (`ms-screenclip:`).
- 🔴 **"adiós"**: Cierra el asistente de voz.

---

## 📐 2. Arquitectura del Sistema

```
                        +----------------------+
                        |   Micrófono (Entrada)|
                        +----------+-----------+
                                   |
                                   v
                      +------------+------------+
                      | SpeechRecognition (STT) |
                      +------------+------------+
                                   | (Texto en español)
                                   v
                      +------------+------------+
                      | Despachador de Comandos |
                      +----+---------------+----+
                           |               |
       +-------------------+               +-------------------+
       |                                                       |
       v                                                       v
+------+----------------+                       +--------------+-------+
| Automatización Windows|                       | Síntesis de Voz (TTS)|
| (calc, notas, web)    |                       | (Respuesta hablada)  |
+-----------------------+                       +----------------------+
```

---

## 🚀 3. Estructura de Archivos

```
TP-Asistente-Voz-Automatizacion/
├── asistente_voz.py   # Script principal del Asistente Virtual
└── README.md          # Documentación del Trabajo Práctico
```

---

## 🛠️ 4. Requisitos e Instalación

### Requisitos Previos:
Instalar las librerías de reconocimiento de voz y audio:
```bash
pip install SpeechRecognition pyttsx3 pyaudio sounddevice numpy
```

### Ejecución:
```bash
python asistente_voz.py
```
