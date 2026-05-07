from app.db import get_db_connection
from app.repositorios.inventario.servicio_repository import ServicioRepository

class ServicioService:
    
    def obtener_todos(self):
        conn = get_db_connection()
        if not conn: return []
        try:
            repo = ServicioRepository(conn)
            return repo.obtener_todos()
        finally:
            conn.close()

    def guardar_servicio(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        
        try:
            conn.autocommit = False
            repo = ServicioRepository(conn)
            
            if data.get('id_servicio'):
                repo.actualizar(data)
            else:
                repo.insertar(data)
                
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (ServicioService): {str(e)}")
            return {'success': False, 'message': 'Error interno al guardar el servicio.'}
        finally:
            conn.close()

    def eliminar_servicio(self, id_servicio):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        
        try:
            conn.autocommit = False
            repo = ServicioRepository(conn)
            repo.eliminar(id_servicio)
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (ServicioService): {str(e)}")
            return {'success': False, 'message': 'El servicio tiene ventas asociadas y no puede eliminarse.'}
        finally:
            conn.close()