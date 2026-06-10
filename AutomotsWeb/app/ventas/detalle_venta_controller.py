from flask import Blueprint, jsonify, request, session
from app.servicios.ventas.detalle_venta_service import DetalleVentaService

detalle_venta_bp = Blueprint('detalle_venta', __name__, url_prefix='/detalle-venta')


@detalle_venta_bp.route('/venta/<int:id_venta>', methods=['GET'])
def obtener_detalles_por_venta(id_venta):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 401

    resultado = DetalleVentaService().obtener_detalles_por_venta(id_venta)
    return jsonify(resultado)


@detalle_venta_bp.route('/registrar/<int:id_venta>', methods=['POST'])
def registrar_detalle_vehiculo(id_venta):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 401

    item = request.get_json()
    resultado = DetalleVentaService().registrar_detalle_vehiculo(id_venta, item)
    return jsonify(resultado)