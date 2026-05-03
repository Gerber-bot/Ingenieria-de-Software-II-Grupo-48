class ServicioRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_servicio, nombre, descripcion, precio, estado FROM Servicio ORDER BY nombre")
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def insertar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Servicio (nombre, descripcion, precio, estado) VALUES (?, ?, ?, ?)
        """, (data['nombre'], data['descripcion'], data['precio'], data['estado']))

    def actualizar(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Servicio SET nombre=?, descripcion=?, precio=?, estado=? WHERE id_servicio=?
        """, (data['nombre'], data['descripcion'], data['precio'], data['estado'], data['id_servicio']))

    def eliminar(self, id_servicio):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Servicio WHERE id_servicio=?", (id_servicio,))