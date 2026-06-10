from abc import ABC, abstractmethod


class ValidacionPagoException(Exception):
    pass


class EstrategiaPago(ABC):

    @abstractmethod
    def validar(self, data: dict, total_oficial_bd: float) -> None:
        pass


class PagoContado(EstrategiaPago):

    def validar(self, data: dict, total_oficial_bd: float) -> None:
        monto_frontend = float(data.get("total_venta", 0))

        if abs(monto_frontend - total_oficial_bd) > 1:
            raise ValidacionPagoException(
                f"Alerta de Seguridad: El monto enviado (${monto_frontend:.2f}) "
                f"difiere del valor oficial (${total_oficial_bd:.2f})."
            )

        if data.get("plan_cuotas"):
            raise ValidacionPagoException(
                "No se puede registrar un plan de cuotas en una venta al contado."
            )


class PagoFinanciado(EstrategiaPago):

    def validar(self, data: dict, total_oficial_bd: float) -> None:
        cuotas = int(data.get("cuotas", 0))
        monto_frontend = float(data.get("total_venta", 0))
        entrega_inicial = float(data.get("entrega_inicial", 0))
        monto_financiado = float(data.get("monto_financiado", 0))
        valor_cuota = float(data.get("valor_cuota", 0))
        tasa_interes = float(data.get("tasa_interes", 0))
        plan_cuotas = data.get("plan_cuotas", [])

        if abs(monto_frontend - total_oficial_bd) > 1:
            raise ValidacionPagoException(
                f"Alerta de Seguridad: El monto enviado (${monto_frontend:.2f}) "
                f"difiere del valor oficial (${total_oficial_bd:.2f})."
            )

        if cuotas < 2 or cuotas > 60:
            raise ValidacionPagoException(
                "Financiación inválida: las cuotas deben estar entre 2 y 60."
            )

        if entrega_inicial < 0:
            raise ValidacionPagoException(
                "Financiación inválida: la entrega inicial no puede ser negativa."
            )

        if entrega_inicial > total_oficial_bd:
            raise ValidacionPagoException(
                "Financiación inválida: la entrega inicial no puede superar el total de la venta."
            )

        monto_esperado = total_oficial_bd - entrega_inicial

        if abs(monto_financiado - monto_esperado) > 1:
            raise ValidacionPagoException(
                f"Error de cálculo: monto financiado esperado ${monto_esperado:.2f}, "
                f"pero se recibió ${monto_financiado:.2f}."
            )

        if tasa_interes < 0:
            raise ValidacionPagoException(
                "Financiación inválida: la tasa de interés no puede ser negativa."
            )

        if valor_cuota <= 0:
            raise ValidacionPagoException(
                "Financiación inválida: el valor de la cuota debe ser mayor a cero."
            )

        if not plan_cuotas:
            raise ValidacionPagoException(
                "Financiación inválida: debe existir un plan de cuotas."
            )