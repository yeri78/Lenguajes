# Responsable: Integrante 2 (estructuras y concurrencia)
"""Cálculo de rutas para muchas solicitudes, secuencial o en paralelo (hilos)."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .calculo import calcular_una
from .lista_enlazada import ListaEnlazada


@dataclass(frozen=True)
class Pedido:
    origen: str
    destino: str
    criterio: str


def calcular_rutas_secuencial(red, pedidos):
    """pedidos: lista de Pedido. Devuelve rutas en el mismo orden (None si no hay camino)."""
    return pedidos.transformar(lambda pedido: calcular_una(red, pedido))


def calcular_rutas_concurrente(red, pedidos, hilos=4):
    """Un hilo del pool por pedido; se conserva el orden de entrada.

    Nota: en CPython los hilos comparten el GIL, así que en tareas de CPU casi no aceleran.
    """
    with ThreadPoolExecutor(max_workers=hilos) as pool:
        futuros = pedidos.transformar(lambda pedido: pool.submit(calcular_una, red, pedido))
        return futuros.transformar(lambda futuro: futuro.result())


def calcular_rutas(red, pedidos, concurrente=True, hilos=4):
    if concurrente:
        return calcular_rutas_concurrente(red, pedidos, hilos)
    return calcular_rutas_secuencial(red, pedidos)


__all__ = ["ListaEnlazada", "Pedido", "calcular_rutas", "calcular_rutas_concurrente", "calcular_rutas_secuencial"]