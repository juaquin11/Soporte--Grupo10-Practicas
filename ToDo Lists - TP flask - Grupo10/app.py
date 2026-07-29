import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task

app = Flask(__name__)
# Clave secreta necesaria para utilizar sesiones y mensajes flash
app.secret_key = 'tp_soporte_visual_grupo10_secret_key'

# Configuración de Flask-SQLAlchemy
# Guardamos la base de datos directamente en el directorio del proyecto
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos con la app
db.init_app(app)

# Crear las tablas automáticamente si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Obtener parámetros de filtrado y búsqueda de la URL
    status_filter = request.args.get('status', 'todas')
    priority_filter = request.args.get('priority', 'todas')
    category_filter = request.args.get('category', 'todas')
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'newest')

    # Consulta base con SQLAlchemy
    query = Task.query

    # Filtrado por estado de completado
    if status_filter == 'pendientes':
        query = query.filter(Task.completed == False)
    elif status_filter == 'completadas':
        query = query.filter(Task.completed == True)

    # Filtrado por prioridad
    if priority_filter != 'todas':
        query = query.filter(Task.priority == priority_filter)

    # Filtrado por categoría
    if category_filter != 'todas':
        query = query.filter(Task.category == category_filter)

    # Búsqueda por título o descripción
    if search_query:
        query = query.filter(
            db.or_(
                Task.title.like(f"%{search_query}%"),
                Task.description.like(f"%{search_query}%")
            )
        )

    # Ordenamiento dinámico
    if sort_by == 'newest':
        query = query.order_by(Task.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Task.created_at.asc())
    elif sort_by == 'due_date':
        # Ordenamiento de vencimiento colocándolo al final si no tiene fecha
        query = query.order_by(Task.due_date.is_(None), Task.due_date.asc())
    elif sort_by == 'priority_desc':
        # Ordenamiento personalizado de prioridad: Alta -> Media -> Baja
        from sqlalchemy import case
        query = query.order_by(
            case(
                (Task.priority == 'Alta', 1),
                (Task.priority == 'Media', 2),
                (Task.priority == 'Baja', 3),
                else_=4
            ).asc()
        )

    tasks = query.all()

    # Contadores para estadísticas del dashboard usando consultas agregadas del ORM
    total_tasks = Task.query.count()
    pending_tasks = Task.query.filter_by(completed=False).count()
    completed_tasks = Task.query.filter_by(completed=True).count()

    # Listas de configuración para el formulario y filtros
    categories = ['General', 'Trabajo', 'Estudio', 'Personal', 'Hogar']
    priorities = ['Baja', 'Media', 'Alta']

    # Fecha actual en formato ISO para validar tareas vencidas en la plantilla
    current_time_str = date.today().isoformat()

    return render_template(
        'index.html', 
        tasks=tasks, 
        total=total_tasks, 
        pending=pending_tasks, 
        completed=completed_tasks,
        categories=categories,
        priorities=priorities,
        current_status=status_filter,
        current_priority=priority_filter,
        current_category=category_filter,
        search_query=search_query,
        current_sort=sort_by,
        current_time_str=current_time_str
    )

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'Media')
    category = request.form.get('category', 'General')
    due_date = request.form.get('due_date', '').strip()

    # Validación básica
    if not title:
        flash('El título de la tarea es obligatorio.', 'danger')
        return redirect(url_for('index'))

    # Si la fecha de vencimiento está vacía, guardarla como None
    if not due_date:
        due_date = None

    try:
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            completed=False
        )
        db.session.add(new_task)
        db.session.commit()
        flash('¡Tarea agregada exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al guardar la tarea: {str(e)}', 'danger')

    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = db.get_or_404(Task, task_id)
    
    try:
        # Cambiar el estado completado (booleano)
        task.completed = not task.completed
        db.session.commit()
        
        message = '¡Tarea marcada como completada!' if task.completed else 'Tarea marcada como pendiente.'
        flash(message, 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al actualizar el estado: {str(e)}', 'danger')
        
    return redirect(request.referrer or url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = db.get_or_404(Task, task_id)

    categories = ['General', 'Trabajo', 'Estudio', 'Personal', 'Hogar']
    priorities = ['Baja', 'Media', 'Alta']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Media')
        category = request.form.get('category', 'General')
        due_date = request.form.get('due_date', '').strip()
        completed = True if request.form.get('completed') else False

        if not title:
            flash('El título de la tarea es obligatorio.', 'danger')
            return render_template('edit.html', task=task, categories=categories, priorities=priorities)

        if not due_date:
            due_date = None

        try:
            task.title = title
            task.description = description
            task.priority = priority
            task.category = category
            task.due_date = due_date
            task.completed = completed
            db.session.commit()
            
            flash('¡Tarea actualizada correctamente!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al actualizar la tarea: {str(e)}', 'danger')

    return render_template('edit.html', task=task, categories=categories, priorities=priorities)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada correctamente.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al eliminar la tarea: {str(e)}', 'danger')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
