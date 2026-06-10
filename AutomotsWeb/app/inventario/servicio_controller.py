from flask import Blueprint, request, session, jsonify
from app.servicios.inventario.servicio_service import ServicioService

servicios_bp = Blueprint('servicios', __name__, url_prefix='/servicios')

@servicios_bp.route('/guardar', methods=['POST'])
def guardar_servicio():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(ServicioService().guardar_servicio(request.get_json()))

@servicios_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_servicio(id):
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(ServicioService().eliminar_servicio(id))