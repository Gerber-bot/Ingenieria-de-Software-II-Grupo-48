class VentaRepository:
    def __init__(self, db_connection):
        self.conn = db_connection
        

    def verificar_disponibilidad_vehiculo(self, id_vehiculo):
        cursor = self.conn.cursor()
        cursor.execute("SELECT estado FROM Vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def pagar_cuota(self, id_plan_cuota):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE PlanCuotas SET estado = 'Pagado', fecha_pago = GETDATE() WHERE id_plan_cuota = ?
        """, (id_plan_cuota,))

    def insertar_cabecera(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Venta (id_cliente, id_usuario, fecha, id_medio_pago, total, 
                               entrega_inicial, monto_financiado, cuotas, valor_cuota, tasa_interes)
            OUTPUT INSERTED.id_venta
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['id_cliente'], data['id_vendedor'], data['fecha'], data['id_medio_pago'], data['total_venta'],
            data['entrega_inicial'], data['monto_financiado'], data['cuotas'], data['valor_cuota'], data['tasa_interes']
        ))
        return cursor.fetchone()[0]

    def insertar_detalle_vehiculo(self, id_venta, item):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO DetalleVenta (id_venta, id_vehiculo, cantidad, precio_unit) VALUES (?, ?, ?, ?)
        """, (id_venta, item['id'], item['cantidad'], item['precio']))

    def insertar_detalle_servicio(self, id_venta, item):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO DetalleServicio (id_venta, id_servicio, precio) VALUES (?, ?, ?)
        """, (id_venta, item['id'], item['precio']))

    def insertar_plan_cuotas(self, id_venta, cuota):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO PlanCuotas (id_venta, numero_cuota, fecha_vencimiento, capital, interes, total_cuota, saldo, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')
        """, (id_venta, cuota['numero'], cuota['vencimiento'], cuota['capital'], cuota['interes'], cuota['total'], cuota['saldo']))

    def inicializar_medios_pago(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM MedioPago")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO MedioPago (nombre) VALUES ('Efectivo'), ('Transferencia'), ('Financiado')")

    def obtener_listados_formulario(self):
        cursor = self.conn.cursor()
        datos = {}
        
        cursor.execute("SELECT id_medio_pago, nombre FROM MedioPago ORDER BY id_medio_pago")
        datos['medios_pago'] = [dict(zip([c[0].lower() for c in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_cliente, nombre, apellido, dni FROM Cliente ORDER BY apellido")
        datos['clientes'] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_vehiculo, modelo, patente, precio FROM Vehiculo WHERE estado = 'disponible'")
        datos['vehiculos'] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_servicio, nombre, precio FROM Servicio WHERE estado = 1")
        datos['servicios'] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT id_usuario, nombre, apellido FROM Usuario WHERE is_activo = 1")
        datos['vendedores'] = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]
        
        return datos

    def obtener_historial_ventas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.id_venta, c.nombre + ' ' + c.apellido as cliente, 
                   u.nombre as vendedor, v.fecha, v.total
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            ORDER BY v.fecha DESC
        """)
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def obtener_cabecera_venta(self, id_venta):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.id_venta, v.fecha, c.nombre + ' ' + c.apellido as cliente,
                   u.nombre + ' ' + u.apellido as vendedor, mp.nombre as medio_pago, 
                   v.total, v.entrega_inicial, v.monto_financiado
            FROM Venta v
            JOIN Cliente c ON v.id_cliente = c.id_cliente
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            LEFT JOIN MedioPago mp ON v.id_medio_pago = mp.id_medio_pago
            WHERE v.id_venta = ?
        """, (id_venta,))
        row = cursor.fetchone()
        return dict(zip([column[0] for column in cursor.description], row)) if row else None

    def obtener_detalles_mixtos(self, id_venta):
        cursor = self.conn.cursor()
        items = []
        cursor.execute("""
            SELECT 'Vehículo' as tipo, v.modelo + ' (' + v.patente + ')' as descripcion, 
                   dv.cantidad, dv.precio_unit as precio, (dv.cantidad * dv.precio_unit) as subtotal
            FROM DetalleVenta dv JOIN Vehiculo v ON dv.id_vehiculo = v.id_vehiculo WHERE dv.id_venta = ?
        """, (id_venta,))
        cols = [column[0] for column in cursor.description]
        for r in cursor.fetchall(): items.append(dict(zip(cols, r)))

        cursor.execute("""
            SELECT 'Servicio' as tipo, s.nombre as descripcion, 1 as cantidad, ds.precio as precio, ds.precio as subtotal
            FROM DetalleServicio ds JOIN Servicio s ON ds.id_servicio = s.id_servicio WHERE ds.id_venta = ?
        """, (id_venta,))
        for r in cursor.fetchall(): items.append(dict(zip(cols, r)))
        return items
    
