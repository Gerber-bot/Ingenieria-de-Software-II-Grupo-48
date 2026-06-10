class AuthRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def buscar_usuario_activo(self, credencial):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, r.nombre as rol, u.password_hash 
            FROM Usuario u
            INNER JOIN Rol r ON u.id_rol = r.id_rol
            WHERE (u.dni = ? OR u.email = ?) AND u.is_activo = 1
        """, (credencial, credencial))
        
        row = cursor.fetchone()
        if row:
            # Convertimos la fila a un diccionario para que el Servicio la pueda leer fácil
            cols = [column[0].lower() for column in cursor.description]
            return dict(zip(cols, row))
        return None