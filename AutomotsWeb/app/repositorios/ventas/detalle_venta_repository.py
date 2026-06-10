class DetalleVentaRepository:

    def __init__(self, db_connection):
        self.conn = db_connection

    def insertar_detalle_vehiculo(self, id_venta, item, precio_oficial):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO DetalleVenta (id_venta, id_vehiculo, cantidad, precio_unit)
            VALUES (?, ?, ?, ?)
        """, (
            id_venta,
            item['id'],
            item.get('cantidad', 1),
            precio_oficial
        ))

    def obtener_detalles_por_venta(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                dv.id_detalle,
                dv.id_venta,
                dv.id_vehiculo,
                v.modelo + ' (' + v.patente + ')' AS descripcion,
                dv.cantidad,
                dv.precio_unit,
                dv.subtotal
            FROM DetalleVenta dv
            JOIN Vehiculo v ON dv.id_vehiculo = v.id_vehiculo
            WHERE dv.id_venta = ?
        """, (id_venta,))

        columnas = [columna[0] for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]