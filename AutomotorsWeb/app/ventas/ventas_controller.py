from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
from app.servicios.ventas.venta_service import VentaService

ventas_bp = Blueprint('ventas', __name__, url_prefix='/operaciones')

@ventas_bp.route('/cuotas/pagar', methods=['POST'])
def pagar_cuota():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(VentaService().pagar_cuota(request.get_json().get('id_plan_cuota')))

@ventas_bp.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if 'user_id' not in session: 
        return redirect(url_for('auth.login'))
    service = VentaService()

    if request.method == 'POST':
        return jsonify(service.registrar_venta(request.get_json()))

    datos = service.obtener_datos_nueva_venta()
    return render_template('ventas/nueva_venta.html', 
                           clientes=datos.get('clientes', []), 
                           vehiculos=datos.get('vehiculos', []), 
                           servicios=datos.get('servicios', []), 
                           vendedores=datos.get('vendedores', []), 
                           medios_pago=datos.get('medios_pago', []),
                           fecha_actual=datetime.now().strftime('%Y-%m-%d'))

@ventas_bp.route('/ventas')
def historial_ventas():
    if 'user_id' not in session: 
        return redirect(url_for('auth.login'))
    return render_template('ventas/historial.html', ventas=VentaService().obtener_historial_ventas())

@ventas_bp.route('/ventas/detalles/<int:id>')
def detalle_venta(id):
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(VentaService().obtener_detalle_venta(id))