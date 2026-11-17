# Responsable: Integrante 4 (asignación, datos y CLI)
"""Resultado de procesar una solicitud."""
from dataclasses import dataclass


@dataclass
class ResultadoSolicitud:
    solicitud: object
    estado: str            # ASIGNADA | EN_COLA | SIN_RUTA
    ruta: object = None
    vehiculo: str = "-"
    cumple_sla: str = "-"
