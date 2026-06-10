from app.db import get_db_connection
from app.repositorios.clientes.cliente_repository import ClienteRepository

class ClienteService:
    def obtener_clientes(self):
        conn = get_db_connection()
        if not conn: return []
        try:
            return ClienteRepository(conn).obtener_todos()
        finally:
            conn.close()

    def guardar_cliente(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'No hay conexión a BD'}
        try:
            conn.autocommit = False
            repo = ClienteRepository(conn)
            if data.get('id_cliente'): repo.actualizar(data)
            else: repo.insertar(data)
            conn.commit()
            return {'success': True, 'message': 'Cliente guardado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (ClienteService): {str(e)}")
            return {'success': False, 'message': 'Error interno al procesar el cliente.'}
        finally:
            conn.close()

    def eliminar_cliente(self, id_cliente):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            repo = ClienteRepository(conn)
            if repo.contar_ventas(id_cliente) > 0:
                return {'success': False, 'message': 'No se puede eliminar porque tiene ventas registradas.'}
            repo.eliminar(id_cliente)
            conn.commit()
            return {'success': True, 'message': 'Cliente eliminado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (ClienteService): {str(e)}")
            return {'success': False, 'message': 'Error interno al eliminar el cliente.'}
        finally:
            conn.close()

    def obtener_datos_completos(self, id_cliente):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            repo = ClienteRepository(conn)
            cuotas = repo.obtener_cuotas_pendientes(id_cliente)
            compras = repo.obtener_historial_compras(id_cliente)
            return {'success': True, 'cuotas': cuotas, 'compras': compras}
        finally:
            conn.close()