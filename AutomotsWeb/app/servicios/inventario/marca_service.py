from app.db import get_db_connection
from app.repositorios.inventario.marca_repository import MarcaRepository

class MarcaService:
    
    def obtener_todas_con_stock(self):
        conn = get_db_connection()
        if not conn: return []
        try:
            repo = MarcaRepository(conn)
            return repo.obtener_todas_con_stock()
        finally:
            conn.close()

    def guardar_marca(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        
        try:
            conn.autocommit = False 
            repo = MarcaRepository(conn)
            
            if data.get('id_marca'):
                repo.actualizar(data['id_marca'], data['nombre'])
            else:
                repo.insertar(data['nombre'])
                
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (MarcaService): {str(e)}")
            return {'success': False, 'message': 'Error interno al guardar la marca.'}
        finally:
            conn.close()

    def eliminar_marca(self, id_marca):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        
        try:
            conn.autocommit = False
            repo = MarcaRepository(conn)
            repo.eliminar(id_marca)
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (MarcaService): {str(e)}")
            return {'success': False, 'message': 'No se puede eliminar la marca porque tiene vehículos asociados.'}
        finally:
            conn.close()