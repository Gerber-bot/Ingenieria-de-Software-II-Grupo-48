from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.db import get_db_connection

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventario')

@inventory_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    marcas, servicios, vehiculos = [], [], []

    if conn:
        cursor = conn.cursor()
        
        # 1. Marcas con su Stock (Lógica de FrmProductos.cs)
        cursor.execute("""
            SELECT m.id_marca, m.nombre, COUNT(v.id_vehiculo) as stock
            FROM Marca m
            LEFT JOIN Vehiculo v ON m.id_marca = v.id_marca AND v.estado = 'disponible'
            GROUP BY m.id_marca, m.nombre
            ORDER BY m.nombre
        """)
        cols = [column[0] for column in cursor.description]
        marcas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        # 2. Servicios
        cursor.execute("SELECT id_servicio, nombre, descripcion, precio, estado FROM Servicio ORDER BY nombre")
        cols = [column[0] for column in cursor.description]
        servicios = [dict(zip(cols, row)) for row in cursor.fetchall()]

        # 3. Vehículos Completos
        cursor.execute("""
            SELECT 
                v.id_vehiculo, m.nombre as marca, v.id_marca, v.modelo, v.version, v.anio, 
                v.color, v.condicion, v.precio, v.kilometraje, v.estado, v.descripcion, 
                v.tipo_vehiculo, v.vin, v.patente, v.stock
            FROM Vehiculo v
            JOIN Marca m ON v.id_marca = m.id_marca
            ORDER BY m.nombre, v.modelo, v.anio DESC
        """)
        cols = [column[0] for column in cursor.description]
        vehiculos = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
    return render_template('inventory/vehiculos.html', marcas=marcas, servicios=servicios, vehiculos=vehiculos)

# ==================== RUTAS DE MARCAS ====================
@inventory_bp.route('/marcas/guardar', methods=['POST'])
def guardar_marca():
    data = request.get_json()
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if data.get('id_marca'):
                cursor.execute("UPDATE Marca SET nombre=? WHERE id_marca=?", (data['nombre'], data['id_marca']))
            else:
                cursor.execute("INSERT INTO Marca (nombre) VALUES (?)", (data['nombre'],))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            conn.close()

@inventory_bp.route('/marcas/eliminar/<int:id>', methods=['POST'])
def eliminar_marca(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Marca WHERE id_marca=?", (id,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': "No se puede eliminar la marca porque tiene vehículos asociados."})
        finally:
            conn.close()

# ==================== RUTAS DE SERVICIOS ====================
@inventory_bp.route('/servicios/guardar', methods=['POST'])
def guardar_servicio():
    data = request.get_json()
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if data.get('id_servicio'):
                cursor.execute("UPDATE Servicio SET nombre=?, descripcion=?, precio=?, estado=? WHERE id_servicio=?", 
                               (data['nombre'], data['descripcion'], data['precio'], data['estado'], data['id_servicio']))
            else:
                cursor.execute("INSERT INTO Servicio (nombre, descripcion, precio, estado) VALUES (?, ?, ?, ?)", 
                               (data['nombre'], data['descripcion'], data['precio'], data['estado']))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            conn.close()

@inventory_bp.route('/servicios/eliminar/<int:id>', methods=['POST'])
def eliminar_servicio(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Servicio WHERE id_servicio=?", (id,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': "El servicio tiene ventas asociadas."})
        finally:
            conn.close()

# ==================== RUTAS DE VEHICULOS ====================
@inventory_bp.route('/vehiculos/guardar', methods=['POST'])
def guardar_vehiculo():
    data = request.get_json()
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            conn.autocommit = False

            # Insertar o actualizar Vehículo
            if data.get('id_vehiculo'):
                cursor.execute("""
                    UPDATE Vehiculo SET id_marca=?, modelo=?, version=?, anio=?, precio=?, stock=?, 
                    descripcion=?, estado=?, tipo_vehiculo=?, color=?, condicion=?, kilometraje=?, vin=?, patente=?
                    WHERE id_vehiculo=?
                """, (
                    data.get('id_marca'), data.get('modelo'), data.get('version', ''), 
                    data.get('anio'), data.get('precio'), data.get('stock', 1),
                    data.get('descripcion', ''), data.get('estado'), data.get('tipo_vehiculo', ''), 
                    data.get('color', ''), data.get('condicion', ''), data.get('kilometraje', 0), 
                    data.get('vin', ''), data.get('patente'), data.get('id_vehiculo')
                ))
                id_vehiculo = data.get('id_vehiculo')
            else:
                cursor.execute("""
                    INSERT INTO Vehiculo (id_marca, modelo, version, anio, precio, stock, descripcion, estado, 
                    tipo_vehiculo, color, condicion, kilometraje, vin, patente)
                    OUTPUT INSERTED.id_vehiculo
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('id_marca'), data.get('modelo'), data.get('version', ''), 
                    data.get('anio'), data.get('precio'), data.get('stock', 1),
                    data.get('descripcion', ''), data.get('estado'), data.get('tipo_vehiculo', ''), 
                    data.get('color', ''), data.get('condicion', ''), data.get('kilometraje', 0), 
                    data.get('vin', ''), data.get('patente')
                ))
                id_vehiculo = cursor.fetchone()[0]

            # Reemplazar Detalles Técnicos
            cursor.execute("DELETE FROM DetallesVehiculo WHERE id_vehiculo=?", (id_vehiculo,))
            cursor.execute("""
                INSERT INTO DetallesVehiculo (id_vehiculo, motor, tipo_combustible, potencia_cv, torque_nm, cilindrada_cm3,
                tipo_transmision, marchas, traccion, seguridad, confort, exterior, consumo_urbano, consumo_extraurbano, 
                consumo_mixto, largo_mm, ancho_mm, alto_mm, capacidad_baul_l, capacidad_tanque_l, descripcion_estado, 
                evaluacion_mecanica, service_oficial, registro_services)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_vehiculo, data.get('motor', ''), data.get('tipo_combustible', ''), 
                data.get('potencia_cv', ''), data.get('torque_nm', ''), data.get('cilindrada_cm3', ''),
                data.get('tipo_transmision', ''), data.get('marchas', ''), data.get('traccion', ''), 
                data.get('seguridad', ''), data.get('confort', ''), data.get('exterior', ''), 
                data.get('consumo_urbano', 0), data.get('consumo_extraurbano', 0), data.get('consumo_mixto', 0), 
                data.get('largo_mm', 0), data.get('ancho_mm', 0), data.get('alto_mm', 0),
                data.get('capacidad_baul_l', 0), data.get('capacidad_tanque_l', 0), data.get('descripcion_estado', ''), 
                data.get('evaluacion_mecanica', ''), data.get('service_oficial', 0), data.get('registro_services', '')
            ))

            conn.commit()
            return jsonify({'success': True})
        
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': str(e)})
        finally:
            conn.close()
            
@inventory_bp.route('/vehiculos/eliminar/<int:id>', methods=['POST'])
def eliminar_vehiculo(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Vehiculo WHERE id_vehiculo=?", (id,))
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': "No se puede eliminar porque tiene ventas asociadas."})
        finally:
            conn.close()

@inventory_bp.route('/vehiculos/<int:id>/detalles', methods=['GET'])
def obtener_detalles_vehiculo(id):
    conn = get_db_connection()
    detalles = {}
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DetallesVehiculo WHERE id_vehiculo=?", (id,))
        row = cursor.fetchone()
        if row:
            cols = [column[0] for column in cursor.description]
            detalles = dict(zip(cols, row))
        conn.close()
    return jsonify(detalles)