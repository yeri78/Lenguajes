# Responsable: Integrante 1 (modelos y validación)
"""Reglas de negocio compartidas por las tres versiones (Python, JavaScript, Java)."""
from .lista_enlazada import ListaEnlazada
from .validacion import DatosInvalidosError

VELOCIDAD_BASE_KMH = 60.0
COSTO_POR_KM = 2.5


def es_trafico(valor):
    return valor in ("BAJO", "MEDIO", "ALTO")


def es_prioridad(valor):
    return valor in ("CRITICA", "ALTA", "MEDIA", "BAJA")


def es_criterio(valor):
    return valor in ("DISTANCIA", "TIEMPO", "COSTO")


def es_estado_vehiculo(valor):
    return valor in ("DISPONIBLE", "OCUPADO")


def factor_trafico(trafico):
    if trafico == "BAJO":
        return 1.0
    if trafico == "MEDIO":
        return 1.3
    if trafico == "ALTO":
        return 1.7
    raise DatosInvalidosError(f"Tráfico desconocido: {trafico}")


def horas_max_respuesta(prioridad):
    if prioridad == "CRITICA":
        return 1
    if prioridad == "ALTA":
        return 2
    if prioridad == "MEDIA":
        return 8
    if prioridad == "BAJA":
        return 24
    raise DatosInvalidosError(f"Prioridad desconocida: {prioridad}")


def orden_prioridad(prioridad):
    """Menor número = se atiende primero."""
    if prioridad == "CRITICA":
        return 0
    if prioridad == "ALTA":
        return 1
    if prioridad == "MEDIA":
        return 2
    if prioridad == "BAJA":
        return 3
    raise DatosInvalidosError(f"Prioridad desconocida: {prioridad}")


def criterios():
    return ListaEnlazada.desde_iterable(["DISTANCIA", "TIEMPO", "COSTO"])