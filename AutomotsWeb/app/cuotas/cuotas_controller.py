from flask import Blueprint, request, session, jsonify
from app.servicios.cuotas.cuota_service import CuotaService

# Creamos el Blueprint para el módulo de cuotas
cuotas_bp = Blueprint('cuotas', __name__, url_prefix='/cuotas')

@cuotas_bp.route('/pagar', methods=['POST'])
def pagar_cuota():
    # Validación de seguridad: el usuario debe estar logueado
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'}), 401
    
    data = request.get_json()
    id_plan_cuota = data.get('id_plan_cuota')
    
    if not id_plan_cuota:
        return jsonify({'success': False, 'message': 'ID de cuota no proporcionado'}), 400

    # Invocamos al servicio exclusivo de cuotas
    service = CuotaService()
    resultado = service.registrar_pago(id_plan_cuota)
    
    return jsonify(resultado)