from app.db import get_db_connection
from app.repositorios.ventas.detalle_servicio_repository import DetalleServicioRepository
from app.repositorios.inventario.servicio_repository import ServicioRepository


class DetalleServicioService:

    def registrar_detalle_servicio(self, id_venta, item, conn=None):
        conexion_externa = conn is not None

        if not conn:
            conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de conexión a BD",
            }

        try:
            detalle_repo = DetalleServicioRepository(conn)
            servicio_repo = ServicioRepository(conn)

            servicio = servicio_repo.obtener_servicio_para_venta(item["id"])

            if not servicio:
                return {
                    "success": False,
                    "message": "El servicio seleccionado no existe.",
                }

            if not servicio["estado"]:
                return {
                    "success": False,
                    "message": "Alerta: el servicio seleccionado no está activo.",
                }

            precio_oficial = float(servicio["precio"])

            if precio_oficial < 0:
                return {
                    "success": False,
                    "message": "Alerta: el servicio tiene un precio inválido.",
                }

            detalle_repo.insertar_detalle_servicio(id_venta, item, precio_oficial)

            if not conexion_externa:
                conn.commit()

            return {
                "success": True,
                "message": "Detalle de servicio registrado correctamente.",
            }

        except Exception as e:
            if not conexion_externa:
                conn.rollback()

            print(f"LOG ERROR (DetalleServicioService): {str(e)}")

            return {
                "success": False,
                "message": "Error al registrar el detalle de servicio.",
            }

        finally:
            if not conexion_externa and conn:
                conn.close()

    def obtener_detalles_por_venta(self, id_venta):
        conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de conexión a BD",
                "detalles": [],
            }

        try:
            repo = DetalleServicioRepository(conn)
            detalles = repo.obtener_detalles_por_venta(id_venta)

            return {
                "success": True,
                "detalles": detalles,
            }

        except Exception as e:
            print(f"LOG ERROR (DetalleServicioService): {str(e)}")

            return {
                "success": False,
                "message": "Error al obtener los detalles de servicio.",
                "detalles": [],
            }

        finally:
            conn.close()