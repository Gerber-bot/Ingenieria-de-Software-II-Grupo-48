from app.db import get_db_connection
from app.repositorios.ventas.venta_repository import VentaRepository

class VentaService:
    def pagar_cuota(self, id_plan_cuota):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de conexión'}
        try:
            conn.autocommit = False
            VentaRepository(conn).pagar_cuota(id_plan_cuota)
            conn.commit()
            return {'success': True, 'message': 'Pago registrado correctamente'}
        except Exception as e:
            conn.rollback()
            print(f"LOG ERROR (VentaService): {str(e)}")
            return {'success': False, 'message': 'Error interno al procesar el pago.'}
        finally:
            conn.close()

    def registrar_venta(self, data):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'No hay conexión a BD'}
        try:
            conn.autocommit = False
            repo = VentaRepository(conn)
            
            for item in data['detalles']:
                if item['tipo'] == 'Vehículo':
                    estado_actual = repo.verificar_disponibilidad_vehiculo(item['id'])
                    if estado_actual != 'disponible':
                        conn.rollback()
                        return {'success': False, 'message': 'El vehículo seleccionado ya no está disponible.'}
           
            # Guardado Transaccional en el caso de que pase la verificacion
            id_venta = repo.insertar_cabecera(data)
            
            for item in data['detalles']:
                if item['tipo'] == 'Vehículo': 
                    repo.insertar_detalle_vehiculo(id_venta, item)
                elif item['tipo'] == 'Servicio': 
                    repo.insertar_detalle_servicio(id_venta, item)
            
            if data.get('plan_cuotas'):
                for cuota in data['plan_cuotas']:
                    repo.insertar_plan_cuotas(id_venta, cuota)
                    
            conn.commit()
            return {'success': True, 'message': f'Venta #{id_venta} registrada con éxito.', 'id_venta': id_venta}
        except Exception as e:
            conn.rollback()
            # Si dos vendedores realizaron la venta en el mismo milisegundo, 
            # el Trigger de SQL Server lanzará el error y el except lo atrapa.
            print(f"LOG ERROR (VentaService): {str(e)}")
            return {'success': False, 'message': 'Error de concurrencia al registrar la venta.'}
        finally:
            conn.close()

    def obtener_datos_nueva_venta(self):
        conn = get_db_connection()
        if not conn: return {}
        try:
            conn.autocommit = False
            repo = VentaRepository(conn)
            repo.inicializar_medios_pago()
            datos = repo.obtener_listados_formulario()
            conn.commit()
            return datos
        finally:
            conn.close()

    def obtener_historial_ventas(self):
        conn = get_db_connection()
        if not conn: return []
        try:
            return VentaRepository(conn).obtener_historial_ventas()
        finally:
            conn.close()

    def obtener_detalle_venta(self, id_venta):
        conn = get_db_connection()
        if not conn: return {'success': False, 'message': 'Error de BD'}
        try:
            repo = VentaRepository(conn)
            cabecera = repo.obtener_cabecera_venta(id_venta)
            if not cabecera: return {'success': False, 'message': 'Venta no encontrada'}
            items = repo.obtener_detalles_mixtos(id_venta)
            return {'success': True, 'cabecera': cabecera, 'items': items}
        finally:
            conn.close()