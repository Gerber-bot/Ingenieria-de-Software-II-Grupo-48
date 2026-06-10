from flask import Blueprint, jsonify, request, session
from app.servicios.ventas.detalle_servicio_service import DetalleServicioService

detalle_servicio_bp = Blueprint(
    "detalle_servicio",
    __name__,
    url_prefix="/detalle-servicio"
)


@detalle_servicio_bp.route("/venta/<int:id_venta>", methods=["GET"])
def obtener_detalles_por_venta(id_venta):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Sesión expirada"}), 401

    resultado = DetalleServicioService().obtener_detalles_por_venta(id_venta)
    return jsonify(resultado)


@detalle_servicio_bp.route("/registrar/<int:id_venta>", methods=["POST"])
def registrar_detalle_servicio(id_venta):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Sesión expirada"}), 401

    item = request.get_json()
    resultado = DetalleServicioService().registrar_detalle_servicio(id_venta, item)
    return jsonify(resultado)