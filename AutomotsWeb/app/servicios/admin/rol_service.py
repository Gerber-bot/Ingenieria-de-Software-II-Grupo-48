from app.db import get_db_connection
from app.repositorios.admin.rol_repository import RolRepository

class RolService:
    def guardar_rol(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            repo = RolRepository(conn)
            if repo.existe_nombre(data['nombre']):
                return {'success': False, 'message': 'El rol ya existe'}
            repo.insertar(data['nombre'])
            conn.commit()
            return {'success': True, 'message': 'Rol agregado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR: {str(e)}")
            return {'success': False, 'message': 'Error interno al guardar rol.'}
        finally:
            conn.close()

    def eliminar_rol(self, id_rol):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            repo = RolRepository(conn)
            if repo.tiene_usuarios_asignados(id_rol):
                return {'success': False, 'message': 'No se puede eliminar el rol porque tiene usuarios asignados'}
            repo.eliminar(id_rol)
            conn.commit()
            return {'success': True, 'message': 'Rol eliminado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR: {str(e)}")
            return {'success': False, 'message': 'Error interno al eliminar rol.'}
        finally:
            conn.close()