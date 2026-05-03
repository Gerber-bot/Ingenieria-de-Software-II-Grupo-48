from flask import Blueprint, request, session, jsonify
from app.servicios.inventario.marca_service import MarcaService

marcas_bp = Blueprint('marcas', __name__, url_prefix='/marcas')

@marcas_bp.route('/guardar', methods=['POST'])
def guardar_marca():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(MarcaService().guardar_marca(request.get_json()))

@marcas_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_marca(id):
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(MarcaService().eliminar_marca(id))