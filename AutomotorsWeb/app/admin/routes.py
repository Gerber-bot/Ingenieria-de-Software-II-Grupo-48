import os
import hashlib
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.db import get_db_connection
from datetime import datetime

# Creamos el Blueprint para tareas administrativas
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def hash_password(password, salt):
    """Función para encriptar contraseñas (replica tu lógica de C#)[cite: 35]"""
    password_bytes = password.encode('utf-8')
    combined = password_bytes + salt
    return hashlib.sha256(combined).digest()

# ==========================================
# 1. RUTA DE BACKUP (Ya la tenías)
# ==========================================
@admin_bp.route('/backup', methods=['GET', 'POST'])
def backup():
    # Validar que el usuario esté logueado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Validar que SOLO el Administrador pueda hacer backups
    if session.get('user_role') != 'Administrador' and session.get('user_id') != 0:
        flash('Acceso denegado. Solo los administradores pueden generar copias de seguridad.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db_connection()
        if conn:
            try:
                # IMPORTANTE: Para ejecutar BACKUP DATABASE en SQL Server usando pyodbc, 
                # la conexión NO puede estar dentro de una transacción. Por eso activamos autocommit.
                conn.autocommit = True 
                cursor = conn.cursor()

                # Definimos la carpeta destino (Misma lógica que usabas en tu C#)
                backup_dir = r"C:\Backups_Automotors"
                
                # Creamos la carpeta desde Python si no existe
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)

                # Generamos el nombre del archivo con la fecha y hora actual
                fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_bak = f"{backup_dir}\\Automotors_Web_{fecha_str}.bak"

                # Ejecutamos el comando SQL de backup
                query = f"BACKUP DATABASE Automotors TO DISK = '{archivo_bak}' WITH FORMAT, MEDIANAME = 'AutomotorsBackup', NAME = 'Full Backup'"
                cursor.execute(query)

                flash(f'¡Copia de seguridad generada con éxito! Archivo guardado en: {archivo_bak}', 'success')
            
            except Exception as e:
                flash(f'Error al generar el backup (Verifique permisos de escritura de SQL Server): {e}', 'danger')
            finally:
                conn.close()

    return render_template('admin/backup.html')

# ==========================================
# 2. RUTAS DE GESTIÓN DE USUARIOS
# ==========================================
@admin_bp.route('/usuarios')
def usuarios_index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    rol_actual = str(session.get('user_role', '')).lower()
    if rol_actual != 'administrador' and session.get('user_id') != 0:
        flash('No tienes permisos para acceder a la gestión de usuarios.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    usuarios = []
    roles = []

    if conn:
        cursor = conn.cursor()
        
        # SELECCIONAMOS LAS COLUMNAS REALES SIN ALIAS
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, u.dni, u.email, u.is_activo, r.nombre as rol
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            ORDER BY u.apellido, u.nombre
        """)
        # FORZAMOS MINÚSCULAS PARA EVITAR PROBLEMAS
        cols = [column[0].lower() for column in cursor.description]
        usuarios = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_rol, nombre FROM Rol ORDER BY nombre")
        cols = [column[0].lower() for column in cursor.description]
        roles = [dict(zip(cols, row)) for row in cursor.fetchall()]

        conn.close()

    return render_template('users/usuarios.html', usuarios=usuarios, roles=roles)

@admin_bp.route('/usuarios/guardar', methods=['POST'])
def guardar_usuario():
    """Crea o modifica un usuario (Lógica de FrmAgregarUsuario)"""
    if 'user_id' not in session or (session.get('user_role') != 'Administrador' and session.get('user_id') != 0):
        return jsonify({'success': False, 'message': 'Permiso denegado'})

    data = request.get_json()
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar si el email existe
            check_query = "SELECT COUNT(*) FROM Usuario WHERE email = ?"
            params = [data['usuario']]
            if data.get('id_usuario'):
                check_query += " AND id_usuario != ?"
                params.append(data['id_usuario'])
            
            cursor.execute(check_query, params)
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': '❌ Este email ya está registrado. Use otro email.'})

            # Lógica de Guardado (Adaptada al esquema actual sin password_salt)
            if data.get('id_usuario'):
                # Actualizar usuario existente
                if data.get('cambiar_password') and data.get('password'):
                    # Generamos el hash simple en bytes para el campo varbinary
                    pwd_hash = hashlib.sha256(data['password'].encode('utf-8')).digest()
                    cursor.execute("""
                        UPDATE Usuario 
                        SET nombre=?, apellido=?, dni=?, email=?, id_rol=?, password_hash=?
                        WHERE id_usuario=?
                    """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], pwd_hash, data['id_usuario']))
                else:
                    cursor.execute("""
                        UPDATE Usuario 
                        SET nombre=?, apellido=?, dni=?, email=?, id_rol=?
                        WHERE id_usuario=?
                    """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], data['id_usuario']))
            else:
                # Nuevo usuario
                pwd_hash = hashlib.sha256(data['password'].encode('utf-8')).digest()
                cursor.execute("""
                    INSERT INTO Usuario (nombre, apellido, dni, email, id_rol, password_hash, is_activo, fecha_nacimiento) 
                    VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
                """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], pwd_hash))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Usuario guardado correctamente'})
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error SQL: {str(e)}'})
        finally:
            conn.close()
            
@admin_bp.route('/usuarios/eliminar/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    """Eliminación física del usuario (Lógica de BEliminar_Click)[cite: 45]"""
    if 'user_id' not in session or (session.get('user_role') != 'Administrador' and session.get('user_id') != 0):
        return jsonify({'success': False, 'message': 'Permiso denegado'})

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (id_usuario,))
            conn.commit()
            return jsonify({'success': True, 'message': '✅ Usuario eliminado permanentemente.'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'❌ No se pudo eliminar el usuario. Es posible que tenga registros (Ventas, Reparaciones) asociados.'})
        finally:
            conn.close()

@admin_bp.route('/usuarios/toggle_estado/<int:id_usuario>', methods=['POST'])
def toggle_estado(id_usuario):
    rol_actual = str(session.get('user_role', '')).lower()
    if 'user_id' not in session or (rol_actual != 'administrador' and session.get('user_id') != 0):
        return jsonify({'success': False, 'message': 'Permiso denegado'})

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Invierte el estado de manera segura a nivel SQL
            cursor.execute("UPDATE Usuario SET is_activo = CASE WHEN is_activo = 1 THEN 0 ELSE 1 END WHERE id_usuario = ?", (id_usuario,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error SQL: {str(e)}'})
        finally:
            conn.close()

# ==========================================
# 3. RUTAS DE GESTIÓN DE ROLES
# ==========================================
@admin_bp.route('/roles/guardar', methods=['POST'])
def guardar_rol():
    """Agrega un nuevo rol (Lógica de FrmGestionRoles)[cite: 41]"""
    if 'user_id' not in session or (session.get('user_role') != 'Administrador' and session.get('user_id') != 0):
        return jsonify({'success': False, 'message': 'Permiso denegado'})

    data = request.get_json()
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar existencia[cite: 41]
            cursor.execute("SELECT COUNT(*) FROM Rol WHERE nombre = ?", (data['nombre'],))
            if cursor.fetchone()[0] > 0:
                 return jsonify({'success': False, 'message': 'El rol ya existe'})

            cursor.execute("INSERT INTO Rol (nombre) VALUES (?)", (data['nombre'],))
            conn.commit()
            return jsonify({'success': True, 'message': 'Rol agregado correctamente'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            conn.close()

@admin_bp.route('/roles/eliminar/<int:id_rol>', methods=['POST'])
def eliminar_rol(id_rol):
    """Elimina un rol (Lógica de FrmGestionRoles)[cite: 41]"""
    if 'user_id' not in session or (session.get('user_role') != 'Administrador' and session.get('user_id') != 0):
        return jsonify({'success': False, 'message': 'Permiso denegado'})

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar uso[cite: 41]
            cursor.execute("SELECT COUNT(*) FROM Usuario WHERE id_rol = ?", (id_rol,))
            if cursor.fetchone()[0] > 0:
                 return jsonify({'success': False, 'message': 'No se puede eliminar el rol porque tiene usuarios asignados'})

            cursor.execute("DELETE FROM Rol WHERE id_rol=?", (id_rol,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Rol eliminado correctamente'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            conn.close()