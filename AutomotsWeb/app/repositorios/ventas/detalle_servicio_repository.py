class DetalleServicioRepository:

    def __init__(self, db_connection):
        self.conn = db_connection

    def insertar_detalle_servicio(self, id_venta, item, precio_oficial):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO DetalleServicio (
                id_venta,
                id_servicio,
                precio
            )
            VALUES (?, ?, ?)
        """, (
            id_venta,
            item["id"],
            precio_oficial,
        ))

    def obtener_detalles_por_venta(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                ds.id_detalle_servicio,
                ds.id_venta,
                ds.id_servicio,
                s.nombre AS descripcion,
                1 AS cantidad,
                ds.precio,
                ds.precio AS subtotal
            FROM DetalleServicio ds
            JOIN Servicio s ON ds.id_servicio = s.id_servicio
            WHERE ds.id_venta = ?
        """, (id_venta,))

        columnas = [columna[0] for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]