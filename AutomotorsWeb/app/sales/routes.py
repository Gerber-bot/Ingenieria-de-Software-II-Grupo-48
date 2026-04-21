from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.db import get_db_connection
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='/operaciones')

@sales_bp.route('/clientes', methods=['GET'])
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    clientes_list = []
    
    if conn:
        cursor = conn.cursor()
        # Traemos clientes ordenados
        cursor.execute("SELECT id_cliente, dni, nombre, apellido, telefono, email FROM Cliente ORDER BY apellido, nombre")
        columns = [column[0] for column in cursor.description]
        clientes_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

    return render_template('sales/clientes.html', clientes=clientes_list)

@sales_bp.route('/clientes/guardar', methods=['POST'])
def guardar_cliente():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    id_cliente = request.form.get('id_cliente') 
    dni = request.form.get('dni')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    direccion = request.form.get('direccion')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if not id_cliente:
                # Cliente nuevo
                cursor.execute("""
                    INSERT INTO Cliente (dni, nombre, apellido, telefono, email, direccion)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (dni, nombre, apellido, telefono, email, direccion))
            else:
                # Edición de cliente
                cursor.execute("""
                    UPDATE Cliente SET dni=?, nombre=?, apellido=?, telefono=?, email=?, direccion=?
                    WHERE id_cliente=?
                """, (dni, nombre, apellido, telefono, email, direccion, id_cliente))
            conn.commit()
            return jsonify({'success': True, 'message': 'Cliente guardado correctamente'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error de BD: {str(e)}'})
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'No hay conexión a BD'})

@sales_bp.route('/clientes/eliminar/<int:id_cliente>', methods=['POST'])
def eliminar_cliente(id_cliente):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar si tiene ventas
            cursor.execute("SELECT COUNT(*) FROM Venta WHERE id_cliente = ?", (id_cliente,))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'message': 'No se puede eliminar el cliente porque tiene ventas registradas.'})

            # Eliminar
            cursor.execute("DELETE FROM Cliente WHERE id_cliente = ?", (id_cliente,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Cliente eliminado correctamente'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        finally:
            conn.close()
            
@sales_bp.route('/clientes/<int:id_cliente>/datos_completos', methods=['GET'])
def get_datos_cliente(id_cliente):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    conn = get_db_connection()
    cuotas = []
    compras = []
    
    if conn:
        cursor = conn.cursor()
        
        # 1. Obtener Cuotas Pendientes
        cursor.execute("""
            SELECT 
                pc.id_plan_cuota, v.id_venta, pc.numero_cuota, 
                CONVERT(VARCHAR, pc.fecha_vencimiento, 23) as vencimiento, 
                pc.total_cuota, pc.estado
            FROM PlanCuotas pc
            INNER JOIN Venta v ON pc.id_venta = v.id_venta
            WHERE v.id_cliente = ? AND pc.estado = 'Pendiente'
            ORDER BY pc.fecha_vencimiento ASC
        """, (id_cliente,))
        cols = [column[0] for column in cursor.description]
        cuotas = [dict(zip(cols, row)) for row in cursor.fetchall()]

        # 2. Obtener Historial de Compras
        cursor.execute("""
            SELECT 
                v.id_venta, CONVERT(VARCHAR, v.fecha, 23) as fecha, v.total, 
                u.nombre + ' ' + u.apellido as vendedor,
                CASE WHEN v.monto_financiado > 0 THEN 'Financiado' ELSE 'Contado' END as forma_pago
            FROM Venta v
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            WHERE v.id_cliente = ?
            ORDER BY v.fecha DESC
        """, (id_cliente,))
        cols = [column[0] for column in cursor.description]
        compras = [dict(zip(cols, row)) for row in cursor.fetchall()]
        
        conn.close()
        
    return jsonify({'success': True, 'cuotas': cuotas, 'compras': compras})

@sales_bp.route('/cuotas/pagar', methods=['POST'])
def pagar_cuota():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    data = request.get_json()
    id_plan_cuota = data.get('id_plan_cuota')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Actualizamos el estado a Pagado
            cursor.execute("""
                UPDATE PlanCuotas 
                SET estado = 'Pagado', fecha_pago = GETDATE()
                WHERE id_plan_cuota = ?
            """, (id_plan_cuota,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Pago registrado correctamente'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al procesar el pago: {str(e)}'})
        finally:
            conn.close()
    return jsonify({'success': False, 'message': 'Error de conexión'})

@sales_bp.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()

    if request.method == 'POST':
        data = request.get_json()
        
        if conn:
            try:
                cursor = conn.cursor()
                conn.autocommit = False

                # Cabecera de venta
                cursor.execute("""
                    INSERT INTO Venta (id_cliente, id_usuario, fecha, id_medio_pago, total, 
                                       entrega_inicial, monto_financiado, cuotas, valor_cuota, tasa_interes)
                    OUTPUT INSERTED.id_venta
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id_cliente'], data['id_vendedor'], data['fecha'], data['id_medio_pago'], data['total_venta'],
                    data['entrega_inicial'], data['monto_financiado'], data['cuotas'], data['valor_cuota'], data['tasa_interes']
                ))
                id_venta = cursor.fetchone()[0]

                # Detalles
                for item in data['detalles']:
                    if item['tipo'] == 'Vehículo':
                        cursor.execute("""
                            INSERT INTO DetalleVenta (id_venta, id_vehiculo, cantidad, precio_unit)
                            VALUES (?, ?, ?, ?)
                        """, (id_venta, item['id'], item['cantidad'], item['precio']))
                    elif item['tipo'] == 'Servicio':
                        cursor.execute("""
                            INSERT INTO DetalleServicio (id_venta, id_servicio, precio)
                            VALUES (?, ?, ?)
                        """, (id_venta, item['id'], item['precio']))

                # Plan de cuotas
                if data['forma_pago'] == 'Financiado' and 'plan_cuotas' in data:
                    for cuota in data['plan_cuotas']:
                        cursor.execute("""
                            INSERT INTO PlanCuotas (id_venta, numero_cuota, fecha_vencimiento, capital, interes, total_cuota, saldo, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')
                        """, (
                            id_venta, cuota['numero'], cuota['vencimiento'], cuota['capital'], 
                            cuota['interes'], cuota['total'], cuota['saldo']
                        ))

                conn.commit()
                return jsonify({'success': True, 'message': f'Venta #{id_venta} registrada con éxito.', 'id_venta': id_venta})
            
            except Exception as e:
                conn.rollback()
                return jsonify({'success': False, 'message': str(e)})
            finally:
                conn.close()

    # Preparar datos para el formulario GET
    clientes, vehiculos, servicios, vendedores, medios_pago = [], [], [], [], []
    if conn:
        cursor = conn.cursor()
        
        # Verificar e insertar Medios de Pago por defecto si está vacío
        cursor.execute("SELECT COUNT(*) FROM MedioPago")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO MedioPago (nombre) VALUES 
                ('Efectivo'), ('Transferencia'), ('Financiado')
            """)
            conn.commit()

        # Obtener listados
        cursor.execute("SELECT id_medio_pago, nombre FROM MedioPago ORDER BY id_medio_pago")
        cols = [column[0].lower() for column in cursor.description]
        medios_pago = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_cliente, nombre, apellido, dni FROM Cliente ORDER BY apellido")
        cols = [column[0] for column in cursor.description]
        clientes = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_vehiculo, modelo, patente, precio FROM Vehiculo WHERE estado = 'disponible'")
        cols = [column[0] for column in cursor.description]
        vehiculos = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_servicio, nombre, precio FROM Servicio WHERE estado = 1")
        cols = [column[0] for column in cursor.description]
        servicios = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_usuario, nombre, apellido FROM Usuario WHERE is_activo = 1")
        cols = [column[0] for column in cursor.description]
        vendedores = [dict(zip(cols, row)) for row in cursor.fetchall()]
        
        conn.close()

    return render_template('sales/nueva_venta.html', 
                           clientes=clientes, vehiculos=vehiculos, servicios=servicios, 
                           vendedores=vendedores, medios_pago=medios_pago,
                           fecha_actual=datetime.now().strftime('%Y-%m-%d'))

@sales_bp.route('/ventas')
def historial_ventas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    ventas_list = []
    
    if conn:
        cursor = conn.cursor()
        # Listado de ventas
        cursor.execute("""
            SELECT v.id_venta, c.nombre + ' ' + c.apellido as cliente, 
                   u.nombre as vendedor, v.fecha, v.total
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            ORDER BY v.fecha DESC
        """)
        columns = [column[0] for column in cursor.description]
        ventas_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

    return render_template('sales/historial.html', ventas=ventas_list)

@sales_bp.route('/ventas/detalles/<int:id>')
def detalle_venta(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Error de BD'})
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id_venta, v.fecha, c.nombre + ' ' + c.apellido as cliente,
                   u.nombre + ' ' + u.apellido as vendedor, mp.nombre as medio_pago, 
                   v.total, v.entrega_inicial, v.monto_financiado
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            LEFT JOIN MedioPago mp ON v.id_medio_pago = mp.id_medio_pago
            WHERE v.id_venta = ?
        """, (id,))
        row = cursor.fetchone()
        if not row: return jsonify({'success': False, 'message': 'Venta no encontrada'})
        
        cols = [column[0] for column in cursor.description]
        cabecera = dict(zip(cols, row))

        items = []
        cursor.execute("""
            SELECT 'Vehículo' as tipo, v.modelo + ' (' + v.patente + ')' as descripcion, 
                   dv.cantidad, dv.precio_unit as precio, (dv.cantidad * dv.precio_unit) as subtotal
            FROM DetalleVenta dv
            JOIN Vehiculo v ON dv.id_vehiculo = v.id_vehiculo
            WHERE dv.id_venta = ?
        """, (id,))
        cols = [column[0] for column in cursor.description]
        for r in cursor.fetchall(): items.append(dict(zip(cols, r)))

        cursor.execute("""
            SELECT 'Servicio' as tipo, s.nombre as descripcion, 
                   1 as cantidad, ds.precio as precio, ds.precio as subtotal
            FROM DetalleServicio ds
            JOIN Servicio s ON ds.id_servicio = s.id_servicio
            WHERE ds.id_venta = ?
        """, (id,))
        cols = [column[0] for column in cursor.description]
        for r in cursor.fetchall(): items.append(dict(zip(cols, r)))

        return jsonify({'success': True, 'cabecera': cabecera, 'items': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()