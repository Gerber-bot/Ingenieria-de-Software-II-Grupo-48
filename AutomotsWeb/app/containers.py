from dependency_injector import containers, providers

from app.strategies.estrategia_pago import PagoContado, PagoFinanciado


class Container(containers.DeclarativeContainer):

    estrategias_pago = providers.Dict({
        "Contado": providers.Factory(PagoContado),
        "Financiado": providers.Factory(PagoFinanciado),
    })