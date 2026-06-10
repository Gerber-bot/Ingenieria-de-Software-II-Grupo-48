import unittest
from unittest.mock import patch, MagicMock

from app.servicios.inventario.vehiculo_service import VehiculoService


class TestCrearVehiculoExitoso(unittest.TestCase):

    def setUp(self):
        self.servicio = VehiculoService()

    @patch('app.servicios.inventario.vehiculo_service.VehiculoRepository')
    @patch('app.servicios.inventario.vehiculo_service.get_db_connection')
    def test_crear_vehiculo_exitoso(self, mock_get_db_connection, mock_vehiculo_repository):
        conn = MagicMock()
        mock_get_db_connection.return_value = conn

        repo = MagicMock()
        mock_vehiculo_repository.return_value = repo

        repo.insertar_vehiculo.return_value = 1

        datos = {
            'id_marca': 1,
            'modelo': 'Focus',
            'version': 'SE',
            'anio': 2023,
            'precio': 18500000,
            'stock': 1,
            'descripcion': 'Vehículo en excelente estado',
            'estado': 'disponible',
            'tipo_vehiculo': 'Auto',
            'color': 'Azul Marino',
            'condicion': 'Nuevo',
            'kilometraje': 0,
            'vin': '8A1DB2345FT123456',
            'patente': 'AF456WY',
            'motor': '2.0L Duratec',
            'tipo_combustible': 'Nafta',
            'potencia_cv': '170',
            'torque_nm': '200',
            'cilindrada_cm3': '2000',
            'tipo_transmision': 'Automática',
            'marchas': '6',
            'traccion': 'Delantera',
            'seguridad': 'ABS, Airbags',
            'confort': 'Aire acondicionado',
            'exterior': 'Llantas de aleación',
            'consumo_urbano': 8,
            'consumo_extraurbano': 6,
            'consumo_mixto': 7,
            'largo_mm': 4630,
            'ancho_mm': 1780,
            'alto_mm': 1435,
            'capacidad_baul_l': 470,
            'capacidad_tanque_l': 50,
            'descripcion_estado': 'Muy buen estado general',
            'evaluacion_mecanica': 'Aprobada',
            'service_oficial': 1,
            'registro_services': 'Service al día'
        }

        resultado = self.servicio.guardar_vehiculo(datos)
        
        print(f"Resultado obtenido: success={resultado['success']}, mensaje: {resultado['message']}")

        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['message'], 'Vehículo guardado correctamente')

        repo.insertar_vehiculo.assert_called_once_with(datos)
        repo.eliminar_detalles.assert_called_once_with(1)
        repo.insertar_detalles.assert_called_once_with(1, datos)

        conn.commit.assert_called_once()
        conn.rollback.assert_not_called()
        conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)