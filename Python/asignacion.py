# Responsable: Integrante 4 (asignación, datos y CLI)
"""Gestión de flota y asignación de solicitudes por prioridad."""
from dataclasses import dataclass

from .cola_prioridad import ColaPrioridad
from .constantes import horas_max_respuesta, orden_prioridad
from .lista_enlazada import ListaEnlazada
from .resultado_solicitud import ResultadoSolicitud


def _comparar_texto(a, b):
    return -1 if a < b else (1 if a > b else 0)


def por_prioridad(a, b):
    """Críticas primero; a igual prioridad, por id."""
    diferencia = orden_prioridad(a.prioridad) - orden_prioridad(b.prioridad)
    return diferencia if diferencia != 0 else _comparar_texto(a.id, b.id)


@dataclass
class SolicitudRuteada:
    """Solicitud junto con la ruta ya calculada (puede ser None)."""
    solicitud: object
    ruta: object


class GestorFlota:
    def __init__(self, vehiculos):
        self.vehiculos = vehiculos

    def disponibles(self):
        return self.vehiculos.filtrar(lambda v: v.disponible)

    def ocupados(self):
        return self.vehiculos.filtrar(lambda v: not v.disponible)

    def asignar(self, pasajeros):
        """Elige el vehículo disponible más pequeño que alcance (best-fit), lo marca ocupado y lo devuelve (o None)."""
        def menor_capacidad(a, b):
            diferencia = a.capacidad - b.capacidad
            return diferencia if diferencia != 0 else _comparar_texto(a.id, b.id)

        elegido = self.disponibles().filtrar(lambda v: v.capacidad >= pasajeros).minimo(menor_capacidad)
        if elegido is not None:
            elegido.ocupar()
        return elegido


def ordenar_por_prioridad(solicitudes):
    cola = ColaPrioridad(por_prioridad)
    solicitudes.para_cada(cola.encolar)
    ordenadas = ListaEnlazada()
    while not cola.esta_vacia():
        ordenadas.agregar_final(cola.desencolar())
    return ordenadas


def cumple_sla(solicitud, ruta):
    return ruta.tiempo_min <= horas_max_respuesta(solicitud.prioridad) * 60


def asignar_solicitudes(pendientes, flota):
    """pendientes: lista de SolicitudRuteada. Sin camino -> SIN_RUTA; sin vehículo disponible -> EN_COLA."""
    cola = ColaPrioridad(lambda a, b: por_prioridad(a.solicitud, b.solicitud))
    pendientes.para_cada(cola.encolar)
    resultados = ListaEnlazada()
    while not cola.esta_vacia():
        pendiente = cola.desencolar()
        solicitud, ruta = pendiente.solicitud, pendiente.ruta
        if ruta is None:
            resultados.agregar_final(ResultadoSolicitud(solicitud, "SIN_RUTA"))
            continue
        vehiculo = flota.asignar(solicitud.pasajeros)
        if vehiculo is None:
            resultados.agregar_final(ResultadoSolicitud(solicitud, "EN_COLA", ruta))
        else:
            resultados.agregar_final(ResultadoSolicitud(
                solicitud, "ASIGNADA", ruta, vehiculo.id, "SI" if cumple_sla(solicitud, ruta) else "NO"))
    return resultados
