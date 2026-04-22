from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db_connection
import hashlib

# Creamos el Blueprint para el módulo de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        usuario_input = request.form.get('usuario') # Puede ser DNI o Email
        password = request.form.get('password')

        # 1. Acceso de emergencia/Admin por defecto (Misma lógica de tu C#)
        if usuario_input == 'admin' and password == 'admin123':
            session['user_id'] = 0
            session['user_name'] = 'Admin Principal'
            session['user_role'] = 'Administrador'
            return redirect(url_for('index'))

        # 2. Validación real contra SQL Server
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Buscamos por DNI o por EMAIL para que sea más flexible (como en la web moderna)
                cursor.execute("""
                    SELECT u.id_usuario, u.nombre, u.apellido, r.nombre as rol, u.password_hash 
                    FROM Usuario u
                    INNER JOIN Rol r ON u.id_rol = r.id_rol
                    WHERE (u.dni = ? OR u.email = ?) AND u.is_activo = 1
                """, (usuario_input, usuario_input))
                
                user = cursor.fetchone()
                
                if user:
                    # Generamos el hash de la contraseña que escribió el usuario para comparar
                    password_hasheada = hashlib.sha256(password.encode('utf-8')).digest()
                    
                    # Comparamos los bytes del hash (campo varbinary en tu SQL)
                    if user.password_hash == password_hasheada:
                        session['user_id'] = user.id_usuario
                        session['user_name'] = f"{user.nombre} {user.apellido}"
                        session['user_role'] = user.rol
                        return redirect(url_for('index'))
                    else:
                        flash('Contraseña incorrecta.', 'danger')
                else:
                    flash('Usuario no encontrado o inactivo.', 'danger')
            except Exception as e:
                flash(f'Error al validar: {e}', 'danger')
            finally:
                conn.close()
        else:
            flash('Error de conexión a la base de datos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear() # Borramos todos los datos de la sesión
    return redirect(url_for('auth.login'))