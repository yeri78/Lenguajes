# Responsable: Integrante 2 (estructuras y concurrencia)
"""Trabajo que se ejecuta por cada solicitud."""
from .rutas import mejor_ruta, todas_las_rutas


def calcular_una(red, pedido):
    """Enumera las rutas posibles y devuelve la mejor según el criterio (o None)."""
    todas_las_rutas(red, pedido.origen, pedido.destino)
    return mejor_ruta(red, pedido.origen, pedido.destino, pedido.criterio)