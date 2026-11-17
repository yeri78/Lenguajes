# Responsable: Integrante 3 (red, rutas y estadísticas)
"""Camino entre dos ubicaciones con sus totales."""
from dataclasses import dataclass

from .lista_enlazada import ListaEnlazada


@dataclass
class Ruta:
    nodos: ListaEnlazada   # ids de ubicación en orden
    distancia_km: float
    tiempo_min: float
    costo: float

    def texto(self):
        return self.nodos.unir("->")