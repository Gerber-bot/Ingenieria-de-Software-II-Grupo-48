from app.db import get_db_connection
from app.repositorios.cuotas.cuota_repository import CuotaRepository

class CuotaService:
    def registrar_pago(self, id_plan_cuota):
        conn = get_db_connection()
        if not conn: 
            return {'success': False, 'message': 'Error de conexión a BD'}
        
        try:
            conn.autocommit = False
            repo = CuotaRepository(conn)
            
            # Ejecutamos la acción en el repositorio
            repo.registrar_pago(id_plan_cuota)
            
            # Confirmamos la transacción
            conn.commit()
            return {'success': True, 'message': 'Pago de cuota registrado correctamente'}
            
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (CuotaService): {str(e)}")
            return {'success': False, 'message': 'Error interno al procesar el pago de la cuota.'}
        finally:
            if conn:
                conn.close()