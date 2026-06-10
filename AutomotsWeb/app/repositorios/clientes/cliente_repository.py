class ClienteRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def buscar_clientes_para_venta(self, criterio="", limite=10):
        cursor = self.conn.cursor()

        criterio = criterio.strip() if criterio else ""
        busqueda = f"%{criterio}%"
        limite = int(limite)

        cursor.execute(f"""
            SELECT TOP {limite}
                id_cliente,
                nombre,
                apellido,
                dni
            FROM Cliente
            WHERE
                nombre LIKE ?
                OR apellido LIKE ?
                OR dni LIKE ?
                OR nombre + ' ' + apellido LIKE ?
                OR apellido + ' ' + nombre LIKE ?
            ORDER BY apellido, nombre
        """, (
            busqueda,
            busqueda,
            busqueda,
            busqueda,
            busqueda
        ))

        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def insertar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            EXEC dbo.sp_InsertarCliente
                @dni = ?,
                @nombre = ?,
                @apellido = ?,
                @telefono = ?,
                @email = ?,
                @direccion = ?
        """, (
            data.get("dni"),
            data.get("nombre"),
            data.get("apellido"),
            data.get("telefono") or None,
            data.get("email") or None,
            data.get("direccion") or None,
        ))

    def actualizar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            EXEC dbo.sp_ActualizarCliente
                @id_cliente = ?,
                @dni = ?,
                @nombre = ?,
                @apellido = ?,
                @telefono = ?,
                @email = ?,
                @direccion = ?
        """, (
            data.get("id_cliente"),
            data.get("dni"),
            data.get("nombre"),
            data.get("apellido"),
            data.get("telefono") or None,
            data.get("email") or None,
            data.get("direccion") or None,
        ))

    def contar_ventas(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM Venta
            WHERE id_cliente = ?
        """, (id_cliente,))
        return cursor.fetchone()[0]

    def eliminar(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM Cliente
            WHERE id_cliente = ?
        """, (id_cliente,))

    def obtener_cuotas_pendientes(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                pc.id_plan_cuota,
                v.id_venta,
                pc.numero_cuota,
                CONVERT(VARCHAR, pc.fecha_vencimiento, 23) AS vencimiento,
                pc.total_cuota,
                pc.estado
            FROM PlanCuotas pc
            INNER JOIN Venta v ON pc.id_venta = v.id_venta
            WHERE v.id_cliente = ?
              AND pc.estado = 'Pendiente'
            ORDER BY pc.fecha_vencimiento ASC
        """, (id_cliente,))

        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            EXEC dbo.sp_ObtenerClientes
        """)

        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def obtener_historial_compras(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                v.id_venta,
                CONVERT(VARCHAR, v.fecha, 23) AS fecha,
                v.total,
                u.nombre + ' ' + u.apellido AS vendedor,
                CASE 
                    WHEN v.monto_financiado > 0 THEN 'Financiado'
                    ELSE 'Contado'
                END AS forma_pago
            FROM Venta v
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            WHERE v.id_cliente = ?
            ORDER BY v.fecha DESC
        """, (id_cliente,))

        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]