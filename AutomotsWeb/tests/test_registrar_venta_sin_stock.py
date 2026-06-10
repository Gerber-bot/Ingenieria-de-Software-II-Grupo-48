import unittest
from unittest.mock import patch, MagicMock

from app.servicios.ventas.venta_service import VentaService
from app.strategies.estrategia_pago import PagoContado


class TestRegistrarVentaSinStock(unittest.TestCase):

    def setUp(self):
        self.servicio = VentaService()

    @patch('app.servicios.ventas.venta_service.DetalleVentaService')
    @patch('app.servicios.ventas.venta_service.VentaRepository')
    @patch('app.servicios.ventas.venta_service.get_db_connection')
    def test_registrar_venta_sin_stock(
        self,
        mock_get_db_connection,
        mock_venta_repository,
        mock_detalle_venta_service
    ):
        conn = MagicMock()
        mock_get_db_connection.return_value = conn

        repo = MagicMock()
        mock_venta_repository.return_value = repo

        detalle_service = MagicMock()
        mock_detalle_venta_service.return_value = detalle_service

        repo.calcular_total_real.return_value = 10000
        repo.insertar_cabecera.return_value = 1

        detalle_service.registrar_detalle_vehiculo.return_value = {
            'success': False,
            'message': 'Alerta: el vehículo seleccionado no está disponible para la venta.'
        }

        datos = {
            'id_cliente': 123,
            'id_vendedor': 1,
            'fecha': '2026-01-01',
            'id_medio_pago': 1,
            'total_venta': 10000,
            'entrega_inicial': 0,
            'monto_financiado': 0,
            'cuotas': 0,
            'valor_cuota': 0,
            'tasa_interes': 0,
            'detalles': [
                {
                    'tipo': 'Vehículo',
                    'id': 55,
                    'cantidad': 1,
                    'precio': 10000
                }
            ]
        }

        estrategia = PagoContado()
        resultado = self.servicio.registrar_venta(datos, estrategia)
        print(f"Resultado obtenido: success={resultado['success']}, mensaje: {resultado['message']}")

        self.assertFalse(resultado['success'])
        self.assertEqual(
            resultado['message'],
            'Alerta: el vehículo seleccionado no está disponible para la venta.'
        )

        repo.calcular_total_real.assert_called_once_with(datos['detalles'])
        repo.insertar_cabecera.assert_called_once_with(datos)
        detalle_service.registrar_detalle_vehiculo.assert_called_once_with(
            1,
            datos['detalles'][0],
            conn
        )

        repo.insertar_plan_cuotas.assert_not_called()
        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()
        conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
