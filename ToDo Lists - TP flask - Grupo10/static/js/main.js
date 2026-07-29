/**
 * JS Lógica y Micro-interacciones - TaskFlow (TP Grupo 10)
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Auto-desvanecer los mensajes Flash de Flask después de 4 segundos
    const alerts = document.querySelectorAll('.flash-messages-container .alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Usar el componente de Bootstrap para cerrar de manera limpia con transición
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });

    // 2. Confirmación elegante para la eliminación de tareas
    const deleteForms = document.querySelectorAll('.delete-task-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (event) => {
            event.preventDefault(); // Evitar el envío inmediato
            
            const confirmed = confirm('¿Estás seguro de que deseas eliminar esta tarea de manera permanente? Esta acción no se puede deshacer.');
            if (confirmed) {
                form.submit(); // Enviar si se confirma
            }
        });
    });

    // 3. Validación interactiva: fecha de vencimiento en el formulario de creación
    const dueDateInput = document.getElementById('due_date');
    if (dueDateInput) {
        dueDateInput.addEventListener('change', (e) => {
            const selectedDate = new Date(e.target.value);
            const today = new Date();
            // Restablecer horas para comparar solo fechas
            today.setHours(0,0,0,0);
            selectedDate.setHours(0,0,0,0);
            
            // Ajustar diferencia horaria local
            selectedDate.setDate(selectedDate.getDate() + 1);

            if (selectedDate < today) {
                alert('Atención: Has seleccionado una fecha de vencimiento que ya ha pasado.');
            }
        });
    }

});
