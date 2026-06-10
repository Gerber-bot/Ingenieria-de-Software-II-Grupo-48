from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime

from app.servicios.ventas.venta_service import VentaService
from app.strategies.pago_strategy_resolver import PagoStrategyResolver


ventas_bp = Blueprint('ventas', __name__, url_prefix='/operaciones')


@ventas_bp.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    service = VentaService()

    if request.method == 'POST':
        payload = request.get_json()

        medio_pago = payload.get('medio_pago')

        try:
            estrategia = PagoStrategyResolver().obtener_estrategia(medio_pago)
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400

        resultado = service.registrar_venta(payload, estrategia)
        return jsonify(resultado)

    datos = service.obtener_datos_nueva_venta()

    return render_template(
        'ventas/nueva_venta.html',
        medios_pago=datos.get('medios_pago', []),
        fecha_actual=datos.get('fecha_actual', datetime.now().strftime('%Y-%m-%d'))
    )


@ventas_bp.route('/ventas')
def historial_ventas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template(
        'ventas/historial.html',
        ventas=VentaService().obtener_historial_ventas()
    )


@ventas_bp.route('/ventas/buscar', methods=['GET'])
def buscar_ventas_historial():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Sesión expirada'
        }), 401

    criterio = request.args.get('criterio', '')

    resultado = VentaService().buscar_ventas_historial(criterio)
    return jsonify(resultado)


@ventas_bp.route('/ventas/detalles/<int:id>')
def detalle_venta(id):
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Sesión expirada'
        }), 401

    return jsonify(VentaService().obtener_detalle_venta(id))


@ventas_bp.route('/ventas/buscar-datos', methods=['GET'])
def buscar_datos_para_venta():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Sesión expirada'
        }), 401

    tipo = request.args.get('tipo', '')
    criterio = request.args.get('criterio', '')

    resultado = VentaService().buscar_datos_para_venta(tipo, criterio)
    return jsonify(resultado)


@ventas_bp.route('/ventas/cancelar/<int:id_venta>', methods=['POST'])
def cancelar_venta(id_venta):
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Sesión expirada'
        }), 401

    resultado = VentaService().cancelar_venta(id_venta)
    return jsonify(resultado)