# Responsable: Integrante 1 (modelos y validación)
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transporte.fila import Fila
from transporte.modelos import Conexion, Solicitud, Ubicacion, Vehiculo
from transporte.validacion import DatosInvalidosError


class PruebasModelos(unittest.TestCase):
    def test_formula_tiempo_con_trafico_alto(self):
        self.assertAlmostEqual(Conexion("A", "B", 60, "ALTO", 0).tiempo_min(), 102.0)

    def test_formula_costo_incluye_peaje(self):
        self.assertAlmostEqual(Conexion("A", "B", 100, "BAJO", 50).costo(), 300.0)

    def test_validacion_rechaza_distancia_negativa(self):
        with self.assertRaises(DatosInvalidosError):
            Conexion.desde_fila(Fila.de("origen", "A", "destino", "B", "distancia_km", "-5",
                                        "trafico", "BAJO", "peaje", "0"))

    def test_validacion_rechaza_prioridad_desconocida(self):
        with self.assertRaises(DatosInvalidosError):
            Solicitud.desde_fila(Fila.de("id", "X", "origen", "L1", "destino", "L2", "prioridad", "URGENTE",
                                         "criterio", "TIEMPO", "pasajeros", "1"))

    def test_validacion_rechaza_campo_vacio_y_no_numerico(self):
        with self.assertRaises(DatosInvalidosError):
            Ubicacion.desde_fila(Fila.de("id", "", "nombre", "X"))
        with self.assertRaises(DatosInvalidosError):
            Vehiculo.desde_fila(Fila.de("id", "V1", "tipo", "Van", "capacidad", "abc", "estado", "DISPONIBLE"))

    def test_vehiculo_lee_su_conductor_y_cambia_de_estado(self):
        v = Vehiculo.desde_fila(Fila.de("id", "V1", "tipo", "Van", "capacidad", "8",
                                        "estado", "DISPONIBLE", "conductor", "Ana"))
        self.assertEqual(v.conductor, "Ana")
        v.ocupar()
        self.assertFalse(v.disponible)
        v.liberar()
        self.assertTrue(v.disponible)


if __name__ == "__main__":
    unittest.main()

