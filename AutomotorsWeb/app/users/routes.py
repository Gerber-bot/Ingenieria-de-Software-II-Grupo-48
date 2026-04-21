from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.db import get_db_connection
import hashlib

# Creamos el Blueprint para la gestión de usuarios
users_bp = Blueprint('users', __name__, url_prefix='/usuarios')

@users_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Opcional: Proteger la ruta para que solo entre el Administrador
    if session.get('user_role') != 'Administrador' and session.get('user_id') != 0:
        flash('No tienes permisos suficientes para acceder a la gestión de usuarios.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()

    if request.method == 'POST':
        # Capturamos datos del modal
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        email = request.form.get('email')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        id_rol = request.form.get('id_rol')
        password = request.form.get('password')

        # Encriptamos la contraseña con SHA256 para que coincida con tu VARBINARY(256)
        password_hash = hashlib.sha256(password.encode('utf-8')).digest()

        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Usuario (nombre, apellido, dni, email, fecha_nacimiento, id_rol, password_hash, is_activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (nombre, apellido, dni, email, fecha_nacimiento, id_rol, password_hash))
                conn.commit()
                flash('Usuario creado exitosamente.', 'success')
            except Exception as e:
                flash(f'Error al guardar el usuario (¿DNI duplicado?): {e}', 'danger')
            finally:
                conn.close()
            return redirect(url_for('users.index'))

    # Lógica GET: Listar usuarios y roles
    usuarios_list = []
    roles_list = []
    
    if conn:
        cursor = conn.cursor()
        # 1. Traemos los usuarios
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, u.dni, u.email, r.nombre AS rol, u.is_activo
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            ORDER BY u.apellido
        """)
        columnas_u = [column[0] for column in cursor.description]
        usuarios_list = [dict(zip(columnas_u, row)) for row in cursor.fetchall()]

        # 2. Traemos los roles para el ComboBox (Select) del Modal
        cursor.execute("SELECT id_rol, nombre FROM Rol")
        columnas_r = [column[0] for column in cursor.description]
        roles_list = [dict(zip(columnas_r, row)) for row in cursor.fetchall()]
        
        conn.close()

    return render_template('users/usuarios.html', usuarios=usuarios_list, roles=roles_list)