# Responsable: Integrante 4 (asignación, datos y CLI)
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transporte.asignacion import GestorFlota, ordenar_por_prioridad
from transporte.datos import (cargar_red, cargar_solicitudes, cargar_vehiculos, escribir_resultados,
                              leer_csv, raiz_proyecto)
from transporte.lista_enlazada import ListaEnlazada
from transporte.modelos import Vehiculo
from transporte.servicio import procesar
from transporte.validacion import DatosInvalidosError

DATOS = os.path.join(raiz_proyecto(), "data")


class PruebasAsignacion(unittest.TestCase):
    def setUp(self):
        self.red = cargar_red(DATOS)

    def test_las_criticas_se_ordenan_primero(self):
        orden = ordenar_por_prioridad(cargar_solicitudes(DATOS, self.red))
        self.assertEqual(orden.obtener(0).prioridad, "CRITICA")
        self.assertEqual(orden.ultimo().prioridad, "BAJA")

    def test_sin_vehiculo_disponible_queda_en_cola(self):
        resultados, _, _ = procesar(self.red, cargar_vehiculos(DATOS), cargar_solicitudes(DATOS, self.red), False)
        self.assertTrue(resultados.contiene(lambda r: r.estado == "EN_COLA"))

    def test_asignacion_elige_el_vehiculo_mas_pequeno_que_alcanza(self):
        flota = GestorFlota(ListaEnlazada.desde_iterable([Vehiculo("A", "Bus", 30), Vehiculo("B", "Sedan", 4)]))
        self.assertEqual(flota.asignar(3).id, "B")
        self.assertEqual(flota.ocupados().tamano(), 1)
        self.assertIsNone(flota.asignar(100))

    def test_archivo_faltante_lanza_error_de_datos(self):
        with self.assertRaises(DatosInvalidosError):
            leer_csv(os.path.join(DATOS, "no_existe.csv"))

    def test_resultados_coinciden_con_los_esperados(self):
        resultados, _, _ = procesar(self.red, cargar_vehiculos(DATOS), cargar_solicitudes(DATOS, self.red), True)
        with tempfile.TemporaryDirectory() as carpeta:
            temporal = os.path.join(carpeta, "resultados_py_test.csv")
            escribir_resultados(temporal, resultados)
            with open(temporal, encoding="utf-8") as f1, \
                    open(os.path.join(DATOS, "resultados_esperados.csv"), encoding="utf-8") as f2:
                self.assertEqual(f1.read(), f2.read())


if __name__ == "__main__":
    unittest.main()
