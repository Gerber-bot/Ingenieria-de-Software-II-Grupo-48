from flask import Blueprint, jsonify, session
from app.servicios.medios_pago.medio_pago_service import MedioPagoService

medios_pago_bp = Blueprint('medios_pago', __name__, url_prefix='/medios-pago')


@medios_pago_bp.route('/', methods=['GET'])
def obtener_medios_pago():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 401

    resultado = MedioPagoService().obtener_medios_pago()
    return jsonify(resultado)