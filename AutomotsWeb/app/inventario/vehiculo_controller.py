from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.servicios.inventario.vehiculo_service import VehiculoService
from app.servicios.inventario.marca_service import MarcaService
from app.servicios.inventario.servicio_service import ServicioService

vehiculos_bp = Blueprint('vehiculos', __name__, url_prefix='/inventario')

@vehiculos_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    marcas = MarcaService().obtener_todas_con_stock()
    servicios = ServicioService().obtener_todos()
    vehiculos = VehiculoService().obtener_todos()

    return render_template('inventario/vehiculos.html', 
                           marcas=marcas, 
                           servicios=servicios, 
                           vehiculos=vehiculos)

@vehiculos_bp.route('/guardar', methods=['POST'])
def guardar_vehiculo():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(VehiculoService().guardar_vehiculo(request.get_json()))

@vehiculos_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_vehiculo(id):
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    return jsonify(VehiculoService().eliminar_vehiculo(id))

@vehiculos_bp.route('/detalles/<int:id>', methods=['GET'])
def obtener_detalles_vehiculo(id):
    """Obtiene los detalles técnicos de un vehículo para cargarlos en la interfaz"""
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Sesión expirada'})
    
    detalles = VehiculoService().obtener_detalles(id)
    return jsonify(detalles)