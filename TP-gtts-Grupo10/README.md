# Trabajo Práctico: Quiz Interactivo de Soporte Técnico con Síntesis de Voz (TTS)

**Materia:** Soporte / Programación  
**Grupo:** 10  

---

## 📌 1. Descripción del Proyecto

Este trabajo práctico desarrolla un sistema interactivo de **Trivia / Quiz Multimedia** enfocado en conocimientos generales de **Soporte Técnico, Hardware y Sistemas Operativos**.

La aplicación cuenta con una interfaz gráfica (GUI) moderna desarrollada en **Python** con **Tkinter**, integrada con síntesis de voz automática (**Text-to-Speech con gTTS**) y reproducción asíncrona mediante **Pygame Mixer** en hilos de ejecución secundarios (`threading`).

### Características Principales:
- 🔊 **Síntesis de Voz Asíncrona:** Lee automáticamente en voz alta cada pregunta y la retroalimentación al responder, sin congelar ni pausar la interfaz.
- 🎨 **Diseño UI/UX Moderno:** Tema oscuro con tarjeta interactiva, efectos de movimiento al pasar el cursor (*hover*), barra de progreso dinámica e indicador de puntaje.
- 🔄 **Preguntas Aleatorias:** Mezcla las preguntas y opciones en cada partida.
- 💡 **Retroalimentación Educativa:** Brinda explicaciones técnicas tras cada respuesta (correcta o incorrecta).
- 📊 **Pantalla de Resultados:** Calcula el porcentaje de efectividad, otorga un diagnóstico final y permite reiniciar el juego.

---

## 📐 2. Fundamentos Técnicos

### A. Programación Concurrente y Multihilo (`threading`)
Para evitar que la descarga del audio o la lectura por altavoz bloquee el hilo principal de eventos de la GUI (`Tkinter.mainloop`), la síntesis de voz se lanza en un hilo secundario demonio (*daemon thread*):

```python
threading.Thread(target=_run_tts, daemon=True).start()
```

### B. Gestión Dinámica de Archivos y Audio
Utiliza `gTTS` para transformar texto en voz guardando un archivo MP3 temporal único. `pygame.mixer` gestiona la carga y descarga limpia del buffer de audio.

---

## 🚀 3. Estructura de Archivos

```
TP-Quiz-Voz-Interactivo/
├── app.py           # Aplicación principal (GUI, Lógica de Trivia y TTS)
├── preguntas.json   # Base de datos de preguntas de Soporte Técnico
└── README.md        # Documentación del Trabajo Práctico
```

---

## 🛠️ 4. Requisitos e Instrucciones de Uso

### Requisitos Previos:
Tener instalado Python y las librerías `gTTS` y `pygame`:
```bash
pip install gtts pygame
```

### Ejecutar la Aplicación:
```bash
python app.py
```
