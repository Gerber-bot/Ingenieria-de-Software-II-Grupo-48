from flask import Blueprint, render_template, request, session, redirect, url_for
from app.servicios.reportes.reporte_service import ReporteService

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    tipo_reporte = request.form.get('tipo_reporte', 'ventas_fecha')
    fecha_desde = request.form.get('fecha_desde')
    fecha_hasta = request.form.get('fecha_hasta')

    service = ReporteService()
    columnas, resultados, f_desde, f_hasta = service.procesar_reporte(tipo_reporte, fecha_desde, fecha_hasta)

    return render_template('reportes/index.html', 
                           resultados=resultados, 
                           columnas=columnas,
                           tipo_reporte=tipo_reporte,
                           fecha_desde=f_desde,
                           fecha_hasta=f_hasta)