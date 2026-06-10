from app.db import get_db_connection

from app.repositorios.ventas.venta_repository import VentaRepository
from app.repositorios.clientes.cliente_repository import ClienteRepository
from app.repositorios.inventario.vehiculo_repository import VehiculoRepository
from app.repositorios.inventario.servicio_repository import ServicioRepository
from app.repositorios.medios_pago.medio_pago_repository import MedioPagoRepository
from app.repositorios.admin.usuario_repository import UsuarioRepository

from datetime import datetime

from app.servicios.ventas.detalle_venta_service import DetalleVentaService
from app.servicios.ventas.detalle_servicio_service import DetalleServicioService

from app.strategies.estrategia_pago import EstrategiaPago, ValidacionPagoException


class VentaService:

    def registrar_venta(self, data, estrategia: EstrategiaPago):
        conn = get_db_connection()

        if not conn:
            return {"success": False, "message": "No hay conexión a BD"}

        try:
            repo = VentaRepository(conn)

            total_oficial = repo.calcular_total_real(data["detalles"])

            try:
                estrategia.validar(data, total_oficial)
            except ValidacionPagoException as error_seguridad:
                return {"success": False, "message": str(error_seguridad)}

            conn.autocommit = False

            id_venta = repo.insertar_cabecera(data)

            for item in data["detalles"]:
                if item["tipo"] == "Vehículo":
                    resultado_detalle = DetalleVentaService().registrar_detalle_vehiculo(
                        id_venta, item, conn
                    )

                    if not resultado_detalle["success"]:
                        conn.rollback()
                        return resultado_detalle

                elif item["tipo"] == "Servicio":
                    resultado_servicio = DetalleServicioService().registrar_detalle_servicio(
                        id_venta, item, conn
                    )

                    if not resultado_servicio["success"]:
                        conn.rollback()
                        return resultado_servicio

            if data.get("plan_cuotas"):
                for cuota in data["plan_cuotas"]:
                    repo.insertar_plan_cuotas(id_venta, cuota)

            conn.commit()

            return {
                "success": True,
                "message": f"Venta #{id_venta} registrada con éxito.",
                "id_venta": id_venta,
            }

        except Exception as e:
            if conn:
                conn.rollback()

            print(f"LOG ERROR (VentaService): {str(e)}")

            return {
                "success": False,
                "message": "Error de concurrencia al registrar la venta.",
            }

        finally:
            if conn:
                conn.close()

    def obtener_datos_nueva_venta(self):
        conn = get_db_connection()

        if not conn:
            return {
                "medios_pago": [],
                "fecha_actual": datetime.now().strftime("%Y-%m-%d"),
            }

        try:
            medio_pago_repo = MedioPagoRepository(conn)

            medio_pago_repo.inicializar_medios_pago()

            return {
                "medios_pago": medio_pago_repo.obtener_medios_pago(),
                "fecha_actual": datetime.now().strftime("%Y-%m-%d"),
            }

        except Exception as e:
            print(f"LOG ERROR (VentaService): {str(e)}")

            return {
                "medios_pago": [],
                "fecha_actual": datetime.now().strftime("%Y-%m-%d"),
            }

        finally:
            conn.close()

    def buscar_datos_para_venta(self, tipo, criterio):
        conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de conexión a BD",
                "datos": [],
            }

        try:
            criterio = criterio.strip() if criterio else ""

            cliente_repo = ClienteRepository(conn)
            vehiculo_repo = VehiculoRepository(conn)
            servicio_repo = ServicioRepository(conn)
            usuario_repo = UsuarioRepository(conn)

            if tipo == "clientes":
                datos = cliente_repo.buscar_clientes_para_venta(criterio)

            elif tipo == "vehiculos":
                datos = vehiculo_repo.buscar_vehiculos_para_venta(criterio)

            elif tipo == "servicios":
                datos = servicio_repo.buscar_servicios_para_venta(criterio)

            elif tipo == "vendedores":
                datos = usuario_repo.buscar_vendedores_para_venta(criterio)

            else:
                return {
                    "success": False,
                    "message": "Tipo de búsqueda no válido.",
                    "datos": [],
                }

            return {
                "success": True,
                "datos": datos,
            }

        except Exception as e:
            print(f"LOG ERROR (VentaService): {str(e)}")

            return {
                "success": False,
                "message": "Error al buscar datos para venta.",
                "datos": [],
            }

        finally:
            conn.close()

    def obtener_historial_ventas(self):
        conn = get_db_connection()

        if not conn:
            return []

        try:
            repo = VentaRepository(conn)
            return repo.buscar_ventas_historial("", 10)

        finally:
            conn.close()

    def obtener_detalle_venta(self, id_venta):
        conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de BD",
            }

        try:
            repo = VentaRepository(conn)
            cabecera = repo.obtener_cabecera_venta(id_venta)

            if not cabecera:
                return {
                    "success": False,
                    "message": "Venta no encontrada",
                }

            items = repo.obtener_detalles_mixtos(id_venta)

            return {
                "success": True,
                "cabecera": cabecera,
                "items": items,
            }

        finally:
            conn.close()

    def buscar_ventas_historial(self, criterio):
        conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de conexión a BD",
                "ventas": [],
            }

        try:
            repo = VentaRepository(conn)
            ventas = repo.buscar_ventas_historial(criterio, 10)

            return {
                "success": True,
                "ventas": ventas,
            }

        except Exception as e:
            print(f"LOG ERROR (VentaService): {str(e)}")

            return {
                "success": False,
                "message": "Error al buscar ventas.",
                "ventas": [],
            }

        finally:
            conn.close()

    def cancelar_venta(self, id_venta):
        conn = get_db_connection()

        if not conn:
            return {
                "success": False,
                "message": "Error de conexión a BD",
            }

        try:
            conn.autocommit = False

            repo = VentaRepository(conn)

            estado_actual = repo.obtener_estado_venta(id_venta)

            if not estado_actual:
                return {
                    "success": False,
                    "message": "La venta no existe.",
                }

            if estado_actual == "Cancelada":
                return {
                    "success": False,
                    "message": "La venta ya se encuentra cancelada.",
                }

            if repo.tiene_cuotas_pagadas(id_venta):
                return {
                    "success": False,
                    "message": "No se puede cancelar la venta porque tiene cuotas pagadas.",
                }

            repo.cancelar_venta(id_venta)
            repo.restaurar_vehiculos_de_venta(id_venta)
            repo.cancelar_cuotas_pendientes(id_venta)

            conn.commit()

            return {
                "success": True,
                "message": f"Venta #{id_venta} cancelada correctamente.",
            }

        except Exception as e:
            conn.rollback()

            print(f"LOG ERROR (VentaService): {str(e)}")

            return {
                "success": False,
                "message": "Error al cancelar la venta.",
            }

        finally:
            conn.close()