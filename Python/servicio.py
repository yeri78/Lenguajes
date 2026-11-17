# Responsable: Integrante 4 (asignación, datos y CLI)
"""Caso de uso principal: procesar todas las solicitudes del conjunto de datos."""
from .asignacion import GestorFlota, SolicitudRuteada, asignar_solicitudes
from .concurrencia import Pedido, calcular_rutas
from .estadisticas import resumir
from .lista_enlazada import ListaEnlazada


def procesar(red, vehiculos, solicitudes, concurrente=True):
    """Devuelve (resultados, resumen, flota)."""
    # 1) Parte paralelizable: calcular la ruta de cada solicitud.
    pedidos = solicitudes.transformar(lambda s: Pedido(s.origen, s.destino, s.criterio))
    rutas = calcular_rutas(red, pedidos, concurrente)

    # 2) Parte secuencial: asignar vehículos respetando la prioridad.
    pendientes = ListaEnlazada()
    siguiente_ruta = iter(rutas)
    for solicitud in solicitudes:
        pendientes.agregar_final(SolicitudRuteada(solicitud, next(siguiente_ruta)))
    flota = GestorFlota(vehiculos)
    resultados = asignar_solicitudes(pendientes, flota)
    return resultados, resumir(resultados, flota), flota
