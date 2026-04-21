from flask import Blueprint, render_template, request, session, redirect, url_for
from app.db import get_db_connection
from datetime import datetime, timedelta

# Creamos el Blueprint para reportes
reports_bp = Blueprint('reports', __name__, url_prefix='/reportes')

@reports_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Fechas por defecto (Últimos 30 días)
    hoy = datetime.now().strftime('%Y-%m-%d')
    hace_30_dias = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Capturar filtros del formulario
    tipo_reporte = request.form.get('tipo_reporte', 'ventas_fecha')
    fecha_desde = request.form.get('fecha_desde', hace_30_dias)
    fecha_hasta = request.form.get('fecha_hasta', hoy)

    resultados = []
    columnas = []
    conn = get_db_connection()

    if conn:
        cursor = conn.cursor()
        
        try:
            # Lógica según el reporte seleccionado
            if tipo_reporte == 'ventas_fecha':
                cursor.execute("""
                    SELECT v.id_venta AS 'Nro_Operacion', v.fecha AS 'Fecha', 
                           c.nombre + ' ' + c.apellido AS 'Cliente',
                           u.nombre AS 'Vendedor', v.total AS 'Total_Venta'
                    FROM Venta v
                    JOIN Cliente c ON v.id_cliente = c.id_cliente
                    JOIN Usuario u ON v.id_usuario = u.id_usuario
                    WHERE v.fecha BETWEEN ? AND ?
                    ORDER BY v.fecha DESC
                """, (fecha_desde, fecha_hasta))
                
            elif tipo_reporte == 'stock_vehiculos':
                cursor.execute("""
                    SELECT m.nombre AS 'Marca', v.modelo AS 'Modelo', v.version AS 'Version',
                           v.anio AS 'Año', v.estado AS 'Estado', v.precio AS 'Precio'
                    FROM Vehiculo v
                    JOIN Marca m ON v.id_marca = m.id_marca
                    ORDER BY v.estado, m.nombre
                """)
                
            # Si la consulta devuelve datos, extraemos las columnas dinámicamente
            if cursor.description:
                columnas = [column[0].replace('_', ' ') for column in cursor.description]
                resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error en reporte: {e}")
        finally:
            conn.close()

    return render_template('reports/index.html', 
                           resultados=resultados, 
                           columnas=columnas,
                           tipo_reporte=tipo_reporte,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta)