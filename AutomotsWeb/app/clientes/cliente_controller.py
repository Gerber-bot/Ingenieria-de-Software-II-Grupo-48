from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.servicios.clientes.cliente_service import ClienteService

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/', methods=['GET'])
def index():
    """Ruta principal para listar clientes"""
    if 'user_id' not in session: 
        return redirect(url_for('auth.login'))
    return render_template('clientes/clientes.html', clientes=ClienteService().obtener_clientes())

@clientes_bp.route('/guardar', methods=['POST'])
def guardar_cliente():
    """Crea o actualiza un cliente"""
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(ClienteService().guardar_cliente(request.form.to_dict()))

@clientes_bp.route('/eliminar/<int:id_cliente>', methods=['POST'])
def eliminar_cliente(id_cliente):
    """Elimina un cliente si no tiene ventas asociadas"""
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(ClienteService().eliminar_cliente(id_cliente))

@clientes_bp.route('/<int:id_cliente>/datos_completos', methods=['GET'])
def get_datos_cliente(id_cliente):
    """Obtiene historial y cuotas para la vista de detalles"""
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(ClienteService().obtener_datos_completos(id_cliente))