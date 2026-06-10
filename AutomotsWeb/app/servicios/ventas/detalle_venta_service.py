from app.db import get_db_connection
from app.repositorios.ventas.detalle_venta_repository import DetalleVentaRepository
from app.repositorios.inventario.vehiculo_repository import VehiculoRepository


class DetalleVentaService:

    def registrar_detalle_vehiculo(self, id_venta, item, conn=None):
        conexion_externa = conn is not None

        if not conn:
            conn = get_db_connection()

        if not conn:
            return {
                'success': False,
                'message': 'Error de conexión a BD'
            }

        try:
            detalle_repo = DetalleVentaRepository(conn)
            vehiculo_repo = VehiculoRepository(conn)

            vehiculo = vehiculo_repo.obtener_vehiculo_para_venta(item['id'])

            if not vehiculo:
                return {
                    'success': False,
                    'message': 'El vehículo seleccionado no existe.'
                }

            if vehiculo['estado'] != 'disponible':
                return {
                    'success': False,
                    'message': 'Alerta: el vehículo seleccionado no está disponible para la venta.'
                }

            cantidad = int(item.get('cantidad', 1))

            if cantidad != 1:
                return {
                    'success': False,
                    'message': 'Alerta: solo se puede vender una unidad por vehículo.'
                }

            precio_oficial = float(vehiculo['precio'])

            if precio_oficial <= 0:
                return {
                    'success': False,
                    'message': 'Alerta: el vehículo tiene un precio inválido.'
                }

            detalle_repo.insertar_detalle_vehiculo(id_venta, item, precio_oficial)

            if not conexion_externa:
                conn.commit()

            return {
                'success': True,
                'message': 'Detalle de venta registrado correctamente.'
            }

        except Exception as e:
            if not conexion_externa:
                conn.rollback()

            print(f"LOG ERROR (DetalleVentaService): {str(e)}")

            return {
                'success': False,
                'message': 'Error al registrar el detalle de venta.'
            }

        finally:
            if not conexion_externa and conn:
                conn.close()

    def obtener_detalles_por_venta(self, id_venta):
        conn = get_db_connection()

        if not conn:
            return {
                'success': False,
                'message': 'Error de conexión a BD',
                'detalles': []
            }

        try:
            repo = DetalleVentaRepository(conn)
            detalles = repo.obtener_detalles_por_venta(id_venta)

            return {
                'success': True,
                'detalles': detalles
            }

        except Exception as e:
            print(f"LOG ERROR (DetalleVentaService): {str(e)}")

            return {
                'success': False,
                'message': 'Error al obtener los detalles de venta.',
                'detalles': []
            }

        finally:
            conn.close()