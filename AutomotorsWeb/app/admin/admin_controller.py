from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify

from app.servicios.admin.usuario_service import UsuarioService
from app.servicios.admin.rol_service import RolService
from app.servicios.admin.backup_service import BackupService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def validar_admin():
    if 'user_id' not in session:
        return False
    rol = str(session.get('user_role', '')).lower()
    return rol == 'administrador' or session.get('user_id') == 0

# RUTA DE BACKUP
@admin_bp.route('/backup', methods=['GET', 'POST'])
def backup():
    if not validar_admin():
        flash('Acceso denegado. Solo los administradores pueden generar copias.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        resultado = BackupService().generar_backup()
        if resultado['success']:
            flash(resultado['message'], 'success')
        else:
            flash(resultado['message'], 'danger')

    return render_template('admin/backup.html')


#RUTAS DE GESTIÓN DE USUARIOS

@admin_bp.route('/usuarios')
def usuarios_index():
    if not validar_admin():
        flash('No tienes permisos para acceder a la gestión de usuarios.', 'danger')
        return redirect(url_for('index'))

    datos = UsuarioService().obtener_datos_pantalla()
    return render_template('users/usuarios.html', usuarios=datos['usuarios'], roles=datos['roles'])

@admin_bp.route('/usuarios/guardar', methods=['POST'])
def guardar_usuario():
    if not validar_admin(): return jsonify({'success': False, 'message': 'Permiso denegado'})
    return jsonify(UsuarioService().guardar_usuario(request.get_json()))
            
@admin_bp.route('/usuarios/eliminar/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    if not validar_admin(): return jsonify({'success': False, 'message': 'Permiso denegado'})
    return jsonify(UsuarioService().eliminar_usuario(id_usuario))

@admin_bp.route('/usuarios/toggle_estado/<int:id_usuario>', methods=['POST'])
def toggle_estado(id_usuario):
    if not validar_admin(): return jsonify({'success': False, 'message': 'Permiso denegado'})
    return jsonify(UsuarioService().toggle_estado(id_usuario))

#RUTAS DE GESTIÓN DE ROLES

@admin_bp.route('/roles/guardar', methods=['POST'])
def guardar_rol():
    if not validar_admin(): return jsonify({'success': False, 'message': 'Permiso denegado'})
    return jsonify(RolService().guardar_rol(request.get_json()))

@admin_bp.route('/roles/eliminar/<int:id_rol>', methods=['POST'])
def eliminar_rol(id_rol):
    if not validar_admin(): return jsonify({'success': False, 'message': 'Permiso denegado'})
    return jsonify(RolService().eliminar_rol(id_rol))