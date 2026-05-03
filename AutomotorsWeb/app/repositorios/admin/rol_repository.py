class RolRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id_rol, nombre FROM Rol ORDER BY nombre")
        cols = [column[0].lower() for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def existe_nombre(self, nombre):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Rol WHERE nombre = ?", (nombre,))
        return cursor.fetchone()[0] > 0

    def insertar(self, nombre):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Rol (nombre) VALUES (?)", (nombre,))

    def tiene_usuarios_asignados(self, id_rol):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE id_rol = ?", (id_rol,))
        return cursor.fetchone()[0] > 0

    def eliminar(self, id_rol):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Rol WHERE id_rol=?", (id_rol,))