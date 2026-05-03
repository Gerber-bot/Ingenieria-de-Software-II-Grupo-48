class UsuarioRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def obtener_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, u.dni, u.email, u.is_activo, r.nombre as rol
            FROM Usuario u
            JOIN Rol r ON u.id_rol = r.id_rol
            ORDER BY u.apellido, u.nombre
        """)
        cols = [column[0].lower() for column in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def email_existe(self, email, id_usuario=None):
        cursor = self.conn.cursor()
        query = "SELECT COUNT(*) FROM Usuario WHERE email = ?"
        params = [email]
        if id_usuario:
            query += " AND id_usuario != ?"
            params.append(id_usuario)
        cursor.execute(query, params)
        return cursor.fetchone()[0] > 0

    def insertar(self, data, pwd_hash):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Usuario (nombre, apellido, dni, email, id_rol, password_hash, is_activo, fecha_nacimiento) 
            VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
        """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], pwd_hash))

    def actualizar_con_password(self, data, pwd_hash):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Usuario SET nombre=?, apellido=?, dni=?, email=?, id_rol=?, password_hash=? WHERE id_usuario=?
        """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], pwd_hash, data['id_usuario']))

    def actualizar_sin_password(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE Usuario SET nombre=?, apellido=?, dni=?, email=?, id_rol=? WHERE id_usuario=?
        """, (data['nombre'], data['apellido'], data['dni'], data['usuario'], data['id_rol'], data['id_usuario']))

    def eliminar(self, id_usuario):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (id_usuario,))

    def toggle_estado(self, id_usuario):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Usuario SET is_activo = CASE WHEN is_activo = 1 THEN 0 ELSE 1 END WHERE id_usuario = ?", (id_usuario,))