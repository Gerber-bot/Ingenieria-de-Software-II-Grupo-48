class ClienteRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_cliente, dni, nombre, apellido, telefono, email FROM Cliente ORDER BY apellido, nombre")
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def insertar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Cliente (dni, nombre, apellido, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.get('dni'), data.get('nombre'), data.get('apellido'), data.get('telefono'), data.get('email'), data.get('direccion')))

    def actualizar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Cliente SET dni=?, nombre=?, apellido=?, telefono=?, email=?, direccion=?
            WHERE id_cliente=?
        """, (data.get('dni'), data.get('nombre'), data.get('apellido'), data.get('telefono'), data.get('email'), data.get('direccion'), data.get('id_cliente')))

    def contar_ventas(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Venta WHERE id_cliente = ?", (id_cliente,))
        return cursor.fetchone()[0]

    def eliminar(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Cliente WHERE id_cliente = ?", (id_cliente,))

    def obtener_cuotas_pendientes(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pc.id_plan_cuota, v.id_venta, pc.numero_cuota, 
                   CONVERT(VARCHAR, pc.fecha_vencimiento, 23) as vencimiento, 
                   pc.total_cuota, pc.estado
            FROM PlanCuotas pc
            INNER JOIN Venta v ON pc.id_venta = v.id_venta
            WHERE v.id_cliente = ? AND pc.estado = 'Pendiente'
            ORDER BY pc.fecha_vencimiento ASC
        """, (id_cliente,))
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def obtener_historial_compras(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.id_venta, CONVERT(VARCHAR, v.fecha, 23) as fecha, v.total, 
                   u.nombre + ' ' + u.apellido as vendedor,
                   CASE WHEN v.monto_financiado > 0 THEN 'Financiado' ELSE 'Contado' END as forma_pago
            FROM Venta v
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            WHERE v.id_cliente = ?
            ORDER BY v.fecha DESC
        """, (id_cliente,))
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]