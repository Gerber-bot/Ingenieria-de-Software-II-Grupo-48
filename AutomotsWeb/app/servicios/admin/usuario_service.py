import hashlib
from app.db import get_db_connection
from app.repositorios.admin.usuario_repository import UsuarioRepository
from app.repositorios.admin.rol_repository import RolRepository

class UsuarioService:
    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).digest()

    def obtener_datos_pantalla(self):
        conn = get_db_connection()
        if not conn: return {'usuarios': [], 'roles': []}
        try:
            return {
                'usuarios': UsuarioRepository(conn).obtener_todos(),
                'roles': RolRepository(conn).obtener_todos()
            }
        finally:
            conn.close()

    def guardar_usuario(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'No hay conexión a BD'}
        try:
            conn.autocommit = False
            repo = UsuarioRepository(conn)
            
            if repo.email_existe(data['usuario'], data.get('id_usuario')):
                return {'success': False, 'message': '❌ Este email ya está registrado.'}

            if data.get('id_usuario'):
                if data.get('cambiar_password') and data.get('password'):
                    repo.actualizar_con_password(data, self._hash_password(data['password']))
                else:
                    repo.actualizar_sin_password(data)
            else:
                repo.insertar(data, self._hash_password(data['password']))
            
            conn.commit()
            return {'success': True, 'message': 'Usuario guardado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR: {str(e)}")
            return {'success': False, 'message': 'Error interno al guardar usuario.'}
        finally:
            conn.close()

    def eliminar_usuario(self, id_usuario):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            UsuarioRepository(conn).eliminar(id_usuario)
            conn.commit()
            return {'success': True, 'message': '✅ Usuario eliminado permanentemente.'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR: {str(e)}")
            return {'success': False, 'message': '❌ No se pudo eliminar el usuario. Es posible que tenga registros asociados.'}
        finally:
            conn.close()

    def toggle_estado(self, id_usuario):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            UsuarioRepository(conn).toggle_estado(id_usuario)
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR: {str(e)}")
            return {'success': False, 'message': 'Error interno al cambiar estado.'}
        finally:
            conn.close()