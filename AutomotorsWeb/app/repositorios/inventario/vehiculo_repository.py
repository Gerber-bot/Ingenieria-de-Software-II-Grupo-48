class VehiculoRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                v.id_vehiculo, m.nombre as marca, v.id_marca, v.modelo, v.version, v.anio, 
                v.color, v.condicion, v.precio, v.kilometraje, v.estado, v.descripcion, 
                v.tipo_vehiculo, v.vin, v.patente, v.stock
            FROM Vehiculo v
            JOIN Marca m ON v.id_marca = m.id_marca
            ORDER BY m.nombre, v.modelo, v.anio DESC
        """)
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def obtener_detalles(self, id_vehiculo):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM DetallesVehiculo WHERE id_vehiculo=?", (id_vehiculo,))
        row = cursor.fetchone()
        if row:
            cols = [column[0] for column in cursor.description]
            return dict(zip(cols, row))
        return {}

    def insertar_vehiculo(self, data):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO Vehiculo (id_marca, modelo, version, anio, precio, stock, descripcion, estado, 
            tipo_vehiculo, color, condicion, kilometraje, vin, patente)
            OUTPUT INSERTED.id_vehiculo
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            data.get('id_marca'), data.get('modelo'), data.get('version', ''), 
            data.get('anio'), data.get('precio'), data.get('stock', 1),
            data.get('descripcion', ''), data.get('estado'), data.get('tipo_vehiculo', ''), 
            data.get('color', ''), data.get('condicion', ''), data.get('kilometraje', 0), 
            data.get('vin', ''), data.get('patente')
        ))
        return cursor.fetchone()[0]

    def actualizar_vehiculo(self, data):
        cursor = self.conn.cursor()
        query = """
            UPDATE Vehiculo SET id_marca=?, modelo=?, version=?, anio=?, precio=?, stock=?, 
            descripcion=?, estado=?, tipo_vehiculo=?, color=?, condicion=?, kilometraje=?, vin=?, patente=?
            WHERE id_vehiculo=?
        """
        cursor.execute(query, (
            data.get('id_marca'), data.get('modelo'), data.get('version', ''), 
            data.get('anio'), data.get('precio'), data.get('stock', 1),
            data.get('descripcion', ''), data.get('estado'), data.get('tipo_vehiculo', ''), 
            data.get('color', ''), data.get('condicion', ''), data.get('kilometraje', 0), 
            data.get('vin', ''), data.get('patente'), data.get('id_vehiculo')
        ))

    def eliminar_detalles(self, id_vehiculo):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM DetallesVehiculo WHERE id_vehiculo=?", (id_vehiculo,))

    def insertar_detalles(self, id_vehiculo, data):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO DetallesVehiculo (id_vehiculo, motor, tipo_combustible, potencia_cv, torque_nm, cilindrada_cm3,
            tipo_transmision, marchas, traccion, seguridad, confort, exterior, consumo_urbano, consumo_extraurbano, 
            consumo_mixto, largo_mm, ancho_mm, alto_mm, capacidad_baul_l, capacidad_tanque_l, descripcion_estado, 
            evaluacion_mecanica, service_oficial, registro_services)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            id_vehiculo, data.get('motor', ''), data.get('tipo_combustible', ''), 
            data.get('potencia_cv', ''), data.get('torque_nm', ''), data.get('cilindrada_cm3', ''),
            data.get('tipo_transmision', ''), data.get('marchas', ''), data.get('traccion', ''), 
            data.get('seguridad', ''), data.get('confort', ''), data.get('exterior', ''), 
            data.get('consumo_urbano', 0), data.get('consumo_extraurbano', 0), data.get('consumo_mixto', 0), 
            data.get('largo_mm', 0), data.get('ancho_mm', 0), data.get('alto_mm', 0),
            data.get('capacidad_baul_l', 0), data.get('capacidad_tanque_l', 0), data.get('descripcion_estado', ''), 
            data.get('evaluacion_mecanica', ''), data.get('service_oficial', 0), data.get('registro_services', '')
        ))

    def eliminar_vehiculo(self, id_vehiculo):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Vehiculo WHERE id_vehiculo=?", (id_vehiculo,))