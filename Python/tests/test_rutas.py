# Responsable: Integrante 3 (red, rutas y estadísticas)
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transporte.datos import cargar_red, raiz_proyecto
from transporte.modelos import Conexion, Ubicacion
from transporte.red import Red
from transporte.rutas import mejor_ruta, todas_las_rutas
from transporte.validacion import DatosInvalidosError

DATOS = os.path.join(raiz_proyecto(), "data")


def red_dos_puntos():
    red = Red()
    red.registrar_ubicacion(Ubicacion("A", "A"))
    red.registrar_ubicacion(Ubicacion("B", "B"))
    return red


class PruebasRutas(unittest.TestCase):
    def setUp(self):
        self.red = cargar_red(DATOS)

    def test_ruta_mas_corta_directa(self):
        ruta = mejor_ruta(self.red, "L5", "L4", "DISTANCIA")
        self.assertEqual(ruta.texto(), "L5->L4")
        self.assertEqual(ruta.distancia_km, 20)

    def test_hay_varias_rutas_posibles(self):
        self.assertGreaterEqual(todas_las_rutas(self.red, "L1", "L7").tamano(), 2)

    def test_criterios_pueden_dar_rutas_distintas(self):
        corta = mejor_ruta(self.red, "L1", "L7", "DISTANCIA")
        barata = mejor_ruta(self.red, "L1", "L7", "COSTO")
        self.assertLessEqual(corta.distancia_km, barata.distancia_km)
        self.assertLessEqual(barata.costo, corta.costo)

    def test_ubicacion_desconocida_lanza_error(self):
        with self.assertRaises(DatosInvalidosError):
            todas_las_rutas(self.red, "L1", "ZZ")

    def test_conexion_duplicada_se_rechaza(self):
        red = red_dos_puntos()
        red.registrar_conexion(Conexion("A", "B", 10, "BAJO", 0))
        with self.assertRaises(DatosInvalidosError):
            red.registrar_conexion(Conexion("B", "A", 10, "BAJO", 0))

    def test_sin_camino_devuelve_none(self):
        self.assertIsNone(mejor_ruta(red_dos_puntos(), "A", "B", "TIEMPO"))

    def test_cambiar_el_trafico_de_un_tramo_aumenta_el_tiempo(self):
        antes = mejor_ruta(self.red, "L1", "L3", "TIEMPO").tiempo_min
        self.red.cambiar_trafico("L3", "L1", "ALTO")
        self.assertGreater(mejor_ruta(self.red, "L1", "L3", "TIEMPO").tiempo_min, antes)
        with self.assertRaises(DatosInvalidosError):
            self.red.cambiar_trafico("L1", "L3", "LENTO")


if __name__ == "__main__":
    unittest.main()
