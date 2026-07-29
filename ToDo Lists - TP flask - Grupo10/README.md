# TaskFlow: Gestor de Tareas (To-Do List)

**TaskFlow** es una aplicación web de gestión de tareas sencilla, moderna y responsiva desarrollada en Python utilizando Flask y el ORM Flask-SQLAlchemy con base de datos SQLite. Este proyecto fue diseñado como trabajo práctico para la materia **Soporte a la base de datos con programación visual**.

---

## 🚀 Características Principales

- **Tablero de Estadísticas (Dashboard):** Visualiza de un vistazo la cantidad total de tareas, las pendientes y las completadas.
- **Filtros Avanzados y Búsqueda:** Filtra tus tareas dinámicamente por estado (Todas, Pendientes, Completadas), prioridad (Alta, Media, Baja) o categoría (Trabajo, Estudio, Personal, Hogar, General). También incluye buscador por texto en tiempo real.
- **Ordenamiento Inteligente:** Ordena las tareas por fecha de creación (más nuevas/viejas), prioridad o por su fecha de vencimiento.
- **Gestión Completa (CRUD):** 
  - Creación rápida de tareas con validación interactiva.
  - Edición detallada en una interfaz limpia.
  - Cambio de estado veloz (completado/pendiente) desde el tablero principal.
  - Eliminación segura con confirmación del cliente.
- **Diseño Premium y Responsive:** Interfaz moderna y adaptada a cualquier pantalla construida con Bootstrap 5, Bootstrap Icons y fuentes tipográficas elegantes (Google Fonts), optimizada con sombras tridimensionales y micro-transiciones.
- **Validaciones Inteligentes:** Alertas al usuario en caso de intentar agendar tareas vacías o fechas de vencimiento del pasado.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python (versión 3.10 o superior) y **Flask** como framework de desarrollo web.
- **Base de Datos & ORM:** **SQLite** de forma local y **Flask-SQLAlchemy** para la persistencia relacional orientada a objetos.
- **Frontend:** HTML5 (Jinja2 para plantillas), CSS3 personalizado (sombras, gradientes violeta/índigo) y Javascript Vanilla para interactividad del cliente.
- **Librería de Estilo:** Bootstrap 5 y Bootstrap Icons mediante CDN.

---

## 📁 Estructura del Proyecto

```
ToDo Lists - TP flask - Grupo10/
│
├── app.py                  # Servidor y controladores de ruta Flask (API/Rutas)
├── models.py               # Definición del modelo de datos de SQLAlchemy (ORM)
├── requirements.txt        # Dependencias de Python del proyecto
├── .gitignore              # Archivos y carpetas ignorados en el control de versiones
├── README.md               # Documentación general del proyecto (este archivo)
│
├── static/                 # Recursos estáticos de la aplicación
│   ├── css/
│   │   └── style.css       # Hoja de estilos personalizados (diseño visual premium)
│   └── js/
│       └── main.js         # Validaciones, confirmaciones y desvanecimiento de alertas
│
└── templates/              # Vistas HTML (Plantillas Jinja2)
    ├── base.html           # Estructura HTML compartida (navbar, footer, alertas flash)
    ├── index.html          # Panel de control principal y lista de tareas
    └── edit.html           # Formulario dedicado a la edición de una tarea
```

---

## 💻 Configuración e Instalación

Sigue estos sencillos pasos para levantar la aplicación de forma local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/juaquin11/TP-Flask-Grupo10.git
cd TP-Flask-Grupo10
```

### 2. Instalar dependencias
Asegúrate de tener Python instalado y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Iniciar el servidor
Ejecuta el archivo principal:
```bash
python app.py
```

El servidor web se levantará localmente. Abre tu navegador y accede a:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

*Nota: La base de datos `tasks.db` se generará automáticamente en el directorio raíz en su primera ejecución si no existe.*

---

<!-- El trabajo fue realizado con la asistencia de Inteligencia Artificial (IA) -->