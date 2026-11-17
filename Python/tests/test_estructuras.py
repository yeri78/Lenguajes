# Responsable: Integrante 2 (estructuras y concurrencia)
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transporte.cola_prioridad import ColaPrioridad
from transporte.concurrencia import Pedido, calcular_rutas_concurrente, calcular_rutas_secuencial
from transporte.datos import cargar_red, raiz_proyecto
from transporte.lista_enlazada import ListaEnlazada


def ascendente(a, b):
    return a - b


def numeros(*valores):
    return ListaEnlazada.desde_iterable(valores)


class PruebasEstructuras(unittest.TestCase):
    def test_lista_agregar_obtener_y_eliminar_ultimo(self):
        lista = ListaEnlazada()
        lista.agregar_final(1)
        lista.agregar_final(2)
        lista.agregar_inicio(0)
        self.assertEqual(lista.tamano(), 3)
        self.assertEqual(lista.obtener(0), 0)
        self.assertEqual(lista.ultimo(), 2)
        self.assertEqual(lista.eliminar_ultimo(), 2)
        self.assertEqual(lista.ultimo(), 1)

    def test_lista_filtrar_transformar_y_sumar(self):
        lista = numeros(1, 2, 3, 4, 5)
        self.assertEqual(str(lista.filtrar(lambda x: x % 2 == 1)), "[1, 3, 5]")
        self.assertEqual(lista.transformar(lambda x: x * 10).obtener(4), 50)
        self.assertEqual(lista.sumar(lambda x: x), 15)

    def test_lista_ordenada_y_minimo(self):
        lista = numeros(3, 1, 2)
        self.assertEqual(str(lista.ordenada(ascendente)), "[1, 2, 3]")
        self.assertEqual(lista.minimo(ascendente), 1)

    def test_lista_fuera_de_rango_y_vacia_lanzan_error(self):
        with self.assertRaises(IndexError):
            numeros(1).obtener(5)
        with self.assertRaises(IndexError):
            ListaEnlazada().eliminar_ultimo()

    def test_cola_de_prioridad_entrega_primero_el_menor(self):
        cola = ColaPrioridad(ascendente)
        for x in (5, 1, 3):
            cola.encolar(x)
        self.assertEqual([cola.desencolar(), cola.desencolar(), cola.desencolar()], [1, 3, 5])
        self.assertTrue(cola.esta_vacia())

    def test_concurrente_igual_a_secuencial(self):
        red = cargar_red(os.path.join(raiz_proyecto(), "data"))
        pedidos = ListaEnlazada.desde_iterable([Pedido("L1", "L7", "TIEMPO"), Pedido("L5", "L8", "COSTO"),
                                                Pedido("L10", "L9", "DISTANCIA")])

        def a_texto(rutas):
            return rutas.transformar(lambda r: f"{r.texto()}|{r.distancia_km}|{r.tiempo_min}|{r.costo}").unir(";")

        self.assertEqual(a_texto(calcular_rutas_concurrente(red, pedidos)),
                         a_texto(calcular_rutas_secuencial(red, pedidos)))


if __name__ == "__main__":
    unittest.main()
