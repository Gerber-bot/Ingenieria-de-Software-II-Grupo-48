from app.db import get_db_connection
from app.repositorios.inventario.vehiculo_repository import VehiculoRepository

class VehiculoService:
    
    def obtener_todos(self):
        conn = get_db_connection()
        if not conn: return []
        try:
            repo = VehiculoRepository(conn)
            return repo.obtener_todos()
        finally:
            conn.close()

    def obtener_detalles(self, id_vehiculo):
        conn = get_db_connection()
        if not conn: return {}
        try:
            repo = VehiculoRepository(conn)
            return repo.obtener_detalles(id_vehiculo)
        finally:
            conn.close()

    def guardar_vehiculo(self, data):
        conn = get_db_connection()
        if not conn: 
            return {'success': False, 'message': 'No hay conexión a la base de datos'}

        try:
            conn.autocommit = False 
            repo = VehiculoRepository(conn)

            if data.get('id_vehiculo'):
                repo.actualizar_vehiculo(data)
                vehiculo_id = data['id_vehiculo']
            else:
                vehiculo_id = repo.insertar_vehiculo(data)

            repo.eliminar_detalles(vehiculo_id)
            repo.insertar_detalles(vehiculo_id, data)

            conn.commit() # Confirma
            return {'success': True, 'message': 'Vehículo guardado correctamente'}
            
        except Exception as e:
            conn.rollback() # Revierte en caso de error
            print(f"LOG ERROR (VehiculoService): {str(e)}") 
            return {'success': False, 'message': 'Error interno al procesar el vehículo.'}
        finally:
            conn.close()

    def eliminar_vehiculo(self, id_vehiculo):
        conn = get_db_connection()
        if not conn: 
            return {'success': False, 'message': 'No hay conexión a la base de datos'}
            
        try:
            conn.autocommit = False
            repo = VehiculoRepository(conn)
            repo.eliminar_vehiculo(id_vehiculo)
            conn.commit()
            return {'success': True, 'message': 'Vehículo eliminado'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (VehiculoService): {str(e)}")
            return {'success': False, 'message': 'No se puede eliminar porque tiene ventas asociadas.'}
        finally:
            conn.close()