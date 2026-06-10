class MarcaRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todas_con_stock(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.id_marca, m.nombre, COUNT(v.id_vehiculo) as stock
            FROM Marca m
            LEFT JOIN Vehiculo v ON m.id_marca = v.id_marca AND v.estado = 'disponible'
            GROUP BY m.id_marca, m.nombre
            ORDER BY m.nombre
        """)
        cols = [column[0] for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def insertar(self, nombre):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Marca (nombre) VALUES (?)", (nombre,))

    def actualizar(self, id_marca, nombre):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Marca SET nombre=? WHERE id_marca=?", (nombre, id_marca))

    def eliminar(self, id_marca):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Marca WHERE id_marca=?", (id_marca,))