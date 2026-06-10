class ReporteRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_ventas_por_fecha(self, fecha_desde, fecha_hasta):
        cursor = self.conn.cursor()
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
        
        return self._formatear_resultados(cursor)

    def obtener_stock_vehiculos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.nombre AS 'Marca', v.modelo AS 'Modelo', v.version AS 'Version',
                   v.anio AS 'Año', v.estado AS 'Estado', v.precio AS 'Precio'
            FROM Vehiculo v
            JOIN Marca m ON v.id_marca = m.id_marca
            ORDER BY v.estado, m.nombre
        """)
        
        return self._formatear_resultados(cursor)

    def _formatear_resultados(self, cursor):
        """Método de apoyo para extraer columnas y diccionarios dinámicamente"""
        columnas = []
        resultados = []
        if cursor.description:
            columnas = [column[0].replace('_', ' ') for column in cursor.description]
            resultados = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        return columnas, resultados