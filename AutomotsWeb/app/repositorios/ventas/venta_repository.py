class VentaRepository:

    def __init__(self, db_connection):
        self.conn = db_connection

    def calcular_total_real(self, detalles_carrito):
        total_oficial = 0.0
        cursor = self.conn.cursor()

        for item in detalles_carrito:
            if item["tipo"] == "Vehículo":
                cursor.execute(
                    "SELECT precio FROM Vehiculo WHERE id_vehiculo = ?",
                    (item["id"],)
                )
                row = cursor.fetchone()

                if row:
                    total_oficial += float(row[0]) * int(item.get("cantidad", 1))

            elif item["tipo"] == "Servicio":
                cursor.execute(
                    "SELECT precio FROM Servicio WHERE id_servicio = ?",
                    (item["id"],)
                )
                row = cursor.fetchone()

                if row:
                    total_oficial += float(row[0])

        return total_oficial

    def insertar_cabecera(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Venta (
                id_cliente,
                id_usuario,
                fecha,
                id_medio_pago,
                total,
                entrega_inicial,
                monto_financiado,
                cuotas,
                valor_cuota,
                tasa_interes
            )
            OUTPUT INSERTED.id_venta
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id_cliente"],
            data["id_vendedor"],
            data["fecha"],
            data["id_medio_pago"],
            data["total_venta"],
            data["entrega_inicial"],
            data["monto_financiado"],
            data["cuotas"],
            data["valor_cuota"],
            data["tasa_interes"],
        ))

        return cursor.fetchone()[0]

    def insertar_plan_cuotas(self, id_venta, cuota):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO PlanCuotas (
                id_venta,
                numero_cuota,
                fecha_vencimiento,
                capital,
                interes,
                total_cuota,
                saldo,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')
        """, (
            id_venta,
            cuota["numero"],
            cuota["vencimiento"],
            cuota["capital"],
            cuota["interes"],
            cuota["total"],
            cuota["saldo"],
        ))

    def obtener_historial_ventas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                v.id_venta,
                c.nombre + ' ' + c.apellido AS cliente,
                u.nombre AS vendedor,
                v.fecha,
                v.total
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            ORDER BY v.fecha DESC
        """)

        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]

    def obtener_cabecera_venta(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                v.id_venta,
                v.fecha,
                c.nombre + ' ' + c.apellido AS cliente,
                u.nombre + ' ' + u.apellido AS vendedor,
                mp.nombre AS medio_pago,
                v.total,
                v.entrega_inicial,
                v.monto_financiado
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            LEFT JOIN MedioPago mp ON v.id_medio_pago = mp.id_medio_pago
            WHERE v.id_venta = ?
        """, (id_venta,))

        row = cursor.fetchone()

        if not row:
            return None

        columnas = [column[0] for column in cursor.description]
        return dict(zip(columnas, row))

    def obtener_detalles_mixtos(self, id_venta):
        cursor = self.conn.cursor()
        items = []

        cursor.execute("""
            SELECT 
                'Vehículo' AS tipo,
                v.modelo + ' (' + v.patente + ')' AS descripcion,
                dv.cantidad,
                dv.precio_unit AS precio,
                dv.subtotal
            FROM DetalleVenta dv
            JOIN Vehiculo v ON dv.id_vehiculo = v.id_vehiculo
            WHERE dv.id_venta = ?
        """, (id_venta,))

        columnas = [column[0] for column in cursor.description]

        for row in cursor.fetchall():
            items.append(dict(zip(columnas, row)))

        cursor.execute("""
            SELECT 
                'Servicio' AS tipo,
                s.nombre AS descripcion,
                1 AS cantidad,
                ds.precio AS precio,
                ds.precio AS subtotal
            FROM DetalleServicio ds
            JOIN Servicio s ON ds.id_servicio = s.id_servicio
            WHERE ds.id_venta = ?
        """, (id_venta,))

        columnas = [column[0] for column in cursor.description]

        for row in cursor.fetchall():
            items.append(dict(zip(columnas, row)))

        return items
    
    def buscar_ventas_historial(self, criterio="", limite=10):
        cursor = self.conn.cursor()

        criterio = criterio.strip() if criterio else ""
        busqueda = f"%{criterio}%"
        limite = int(limite)

        cursor.execute(f"""
            SELECT TOP {limite}
                v.id_venta,
                c.nombre + ' ' + c.apellido AS cliente,
                u.nombre + ' ' + u.apellido AS vendedor,
                v.fecha,
                v.total,
                v.estado
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            WHERE
                CAST(v.id_venta AS VARCHAR) LIKE ?
                OR c.nombre LIKE ?
                OR c.apellido LIKE ?
                OR c.nombre + ' ' + c.apellido LIKE ?
                OR c.apellido + ' ' + c.nombre LIKE ?
                OR u.nombre LIKE ?
                OR u.apellido LIKE ?
                OR u.nombre + ' ' + u.apellido LIKE ?
                OR CONVERT(VARCHAR, v.fecha, 23) LIKE ?
                OR v.estado LIKE ?
            ORDER BY v.fecha DESC
        """, (
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda
        ))

        columnas = [column[0] for column in cursor.description]
        return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    
    def obtener_estado_venta(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT estado
            FROM Venta
            WHERE id_venta = ?
        """, (id_venta,))

        row = cursor.fetchone()

        if not row:
            return None

        return row[0]

    def tiene_cuotas_pagadas(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM PlanCuotas
            WHERE id_venta = ?
              AND estado = 'Pagado'
        """, (id_venta,))

        return cursor.fetchone()[0] > 0

    def cancelar_venta(self, id_venta):
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE Venta
            SET estado = 'Cancelada'
            WHERE id_venta = ?
        """, (id_venta,))

    def restaurar_vehiculos_de_venta(self, id_venta):
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE Vehiculo
            SET estado = 'disponible'
            WHERE id_vehiculo IN (
                SELECT id_vehiculo
                FROM DetalleVenta
                WHERE id_venta = ?
            )
        """, (id_venta,))

    def cancelar_cuotas_pendientes(self, id_venta):
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE PlanCuotas
            SET estado = 'Cancelada'
            WHERE id_venta = ?
              AND estado = 'Pendiente'
        """, (id_venta,))