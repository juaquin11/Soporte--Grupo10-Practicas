from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    """Modelo de base de datos para representar una tarea (Task)."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Media')    # 'Alta', 'Media', 'Baja'
    category = db.Column(db.String(30), nullable=False, default='General')  # 'Trabajo', 'Estudio', 'Personal', 'Hogar', 'General'
    completed = db.Column(db.Boolean, nullable=False, default=False)
    due_date = db.Column(db.String(10), nullable=True)                      # Formato YYYY-MM-DD
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'
