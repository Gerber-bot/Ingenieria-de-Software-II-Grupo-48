from app.containers import Container


class PagoStrategyResolver:

    def __init__(self):
        self.container = Container()

    def obtener_estrategia(self, medio_pago):
        estrategias = self.container.estrategias_pago()

        estrategia = estrategias.get(medio_pago)

        if not estrategia:
            raise ValueError(f'Medio de pago "{medio_pago}" no soportado por el sistema.')

        return estrategia