import unittest
from unittest.mock import patch, MagicMock

from app.servicios.inventario.vehiculo_service import VehiculoService


class TestCrearVehiculoError(unittest.TestCase):

    def setUp(self):
        self.servicio = VehiculoService()

    @patch('app.servicios.inventario.vehiculo_service.VehiculoRepository')
    @patch('app.servicios.inventario.vehiculo_service.get_db_connection')
    def test_crear_vehiculo_error_vin_duplicado(self, mock_get_db_connection, mock_vehiculo_repository):
        conn = MagicMock()
        mock_get_db_connection.return_value = conn

        repo = MagicMock()
        mock_vehiculo_repository.return_value = repo

        repo.insertar_vehiculo.side_effect = Exception('Violación de clave única en VIN')

        datos = {
            'id_marca': 2,
            'modelo': 'Cruze',
            'version': 'LT',
            'anio': 2022,
            'precio': 17000000,
            'stock': 1,
            'descripcion': 'Vehículo con VIN duplicado',
            'estado': 'disponible',
            'tipo_vehiculo': 'Auto',
            'color': 'Blanco',
            'condicion': 'Usado',
            'kilometraje': 25000,
            'vin': '8A1DB2345FT123456',
            'patente': 'AG789LK',
            'motor': '1.4L Turbo',
            'tipo_combustible': 'Nafta',
            'potencia_cv': '153',
            'torque_nm': '245',
            'cilindrada_cm3': '1400',
            'tipo_transmision': 'Manual',
            'marchas': '6',
            'traccion': 'Delantera',
            'seguridad': 'ABS, Airbags',
            'confort': 'Aire acondicionado',
            'exterior': 'Llantas de aleación',
            'consumo_urbano': 8,
            'consumo_extraurbano': 6,
            'consumo_mixto': 7,
            'largo_mm': 4666,
            'ancho_mm': 1807,
            'alto_mm': 1484,
            'capacidad_baul_l': 440,
            'capacidad_tanque_l': 52,
            'descripcion_estado': 'Buen estado',
            'evaluacion_mecanica': 'Aprobada',
            'service_oficial': 1,
            'registro_services': 'Service al día'
        }

        resultado = self.servicio.guardar_vehiculo(datos)
        
        print(f"Resultado obtenido: success={resultado['success']}, mensaje: {resultado['message']}")

        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Error interno al procesar el vehículo.')

        repo.insertar_vehiculo.assert_called_once_with(datos)
        repo.eliminar_detalles.assert_not_called()
        repo.insertar_detalles.assert_not_called()

        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()
        conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)