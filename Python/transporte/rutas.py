# Responsable: Integrante 3 (red, rutas y estadísticas)
"""Búsqueda de rutas: todas las rutas simples (recursión) y la mejor (Dijkstra con ColaPrioridad)."""
from dataclasses import dataclass

from .cola_prioridad import ColaPrioridad
from .lista_enlazada import ListaEnlazada
from .ruta import Ruta


def comparar_nodos(a, b):
    siguiente_b = iter(b)
    for x in a:
        y = next(siguiente_b, None)
        if y is None:
            return 1
        if x < y:
            return -1
        if x > y:
            return 1
    return -1 if next(siguiente_b, None) is not None else 0


def construir_ruta(red, nodos):
    """Suma distancia, tiempo y costo recorriendo los tramos en orden."""
    distancia = tiempo = costo = 0.0
    anterior = None
    for nodo in nodos:
        if anterior is not None:
            tramo = red.buscar_conexion(anterior, nodo)
            distancia += tramo.distancia_km
            tiempo += tramo.tiempo_min()
            costo += tramo.costo()
        anterior = nodo
    return Ruta(nodos.copiar(), distancia, tiempo, costo)


def _explorar(red, actual, destino, camino, salida):
    if actual == destino:
        salida.agregar_final(construir_ruta(red, camino))
        return
    for tramo in red.vecinos(actual):
        if not camino.contiene_valor(tramo.destino):
            camino.agregar_final(tramo.destino)
            _explorar(red, tramo.destino, destino, camino, salida)
            camino.eliminar_ultimo()


def todas_las_rutas(red, origen, destino):
    """Todas las rutas simples (sin repetir ubicaciones), ordenadas por su camino."""
    red.validar_ubicacion(origen)
    red.validar_ubicacion(destino)
    encontradas = ListaEnlazada()
    camino = ListaEnlazada()
    camino.agregar_final(origen)
    _explorar(red, origen, destino, camino, encontradas)
    return encontradas.ordenada(lambda a, b: comparar_nodos(a.nodos, b.nodos))


@dataclass
class _Entrada:
    peso: float
    camino: ListaEnlazada


def _comparar_entradas(a, b):
    if a.peso < b.peso:
        return -1
    if a.peso > b.peso:
        return 1
    return comparar_nodos(a.camino, b.camino)


def mejor_ruta(red, origen, destino, criterio):
    """Dijkstra. Desempata por orden lexicográfico del camino (determinista). Devuelve None si no hay ruta."""
    red.validar_ubicacion(origen)
    red.validar_ubicacion(destino)
    frontera = ColaPrioridad(_comparar_entradas)
    inicio = ListaEnlazada()
    inicio.agregar_final(origen)
    frontera.encolar(_Entrada(0.0, inicio))
    visitados = ListaEnlazada()
    while not frontera.esta_vacia():
        actual = frontera.desencolar()
        nodo = actual.camino.ultimo()
        if visitados.contiene_valor(nodo):
            continue
        visitados.agregar_final(nodo)
        if nodo == destino:
            return construir_ruta(red, actual.camino)
        for tramo in red.vecinos(nodo):
            if not visitados.contiene_valor(tramo.destino):
                camino = actual.camino.copiar()
                camino.agregar_final(tramo.destino)
                frontera.encolar(_Entrada(actual.peso + tramo.peso(criterio), camino))
    return None