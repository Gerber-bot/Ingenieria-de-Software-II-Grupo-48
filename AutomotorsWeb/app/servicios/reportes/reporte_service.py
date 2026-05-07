from datetime import datetime, timedelta
from app.db import get_db_connection
from app.repositorios.reportes.reporte_repository import ReporteRepository

class ReporteService:
    def procesar_reporte(self, tipo_reporte, fecha_desde, fecha_hasta):
        if not fecha_desde or not fecha_hasta:
            hoy = datetime.now().strftime('%Y-%m-%d')
            hace_30_dias = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            fecha_desde = fecha_desde or hace_30_dias
            fecha_hasta = fecha_hasta or hoy

        columnas, resultados = [], []
        conn = get_db_connection()
        
        if not conn:
            return columnas, resultados, fecha_desde, fecha_hasta

        try:
            repo = ReporteRepository(conn)
            
            if tipo_reporte == 'ventas_fecha':
                columnas, resultados = repo.obtener_ventas_por_fecha(fecha_desde, fecha_hasta)
            elif tipo_reporte == 'stock_vehiculos':
                columnas, resultados = repo.obtener_stock_vehiculos()
                
        except Exception as e:
            print(f"LOG ERROR (ReporteService): {str(e)}")
        finally:
            conn.close()

        return columnas, resultados, fecha_desde, fecha_hasta