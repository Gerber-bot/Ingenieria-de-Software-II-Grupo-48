from app.db import get_db_connection
from app.repositorios.medios_pago.medio_pago_repository import MedioPagoRepository


class MedioPagoService:

    def obtener_medios_pago(self):
        conn = get_db_connection()

        if not conn:
            return {'success': False, 'message': 'Error de conexión a BD', 'medios_pago': []}

        try:
            repo = MedioPagoRepository(conn)
            repo.inicializar_medios_pago()
            medios_pago = repo.obtener_medios_pago()

            return {
                'success': True,
                'medios_pago': medios_pago
            }

        except Exception as e:
            print(f"LOG ERROR (MedioPagoService): {str(e)}")
            return {'success': False, 'message': 'Error al obtener los medios de pago', 'medios_pago': []}

        finally:
            if conn:
                conn.close()