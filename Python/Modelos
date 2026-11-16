# Responsable: Integrante 1 (modelos y validación)
"""Clases del dominio: Ubicacion, Conexion, Vehiculo y Solicitud."""
from dataclasses import dataclass

from . import constantes as C
from .validacion import (DatosInvalidosError, requerir_entero, requerir_numero,
                         requerir_opcion, requerir_texto)


@dataclass(frozen=True)
class Ubicacion:
    id: str
    nombre: str
    x: float = 0.0
    y: float = 0.0

    @staticmethod
    def desde_fila(fila):
        return Ubicacion(requerir_texto(fila, "id"), requerir_texto(fila, "nombre"),
                         float(fila.obtener_opcional("x", "0")), float(fila.obtener_opcional("y", "0")))


@dataclass(frozen=True)
class Conexion:
    """Tramo entre dos ubicaciones (se usa en ambos sentidos)."""
    origen: str
    destino: str
    distancia_km: float
    trafico: str
    peaje: float

    @staticmethod
    def desde_fila(fila):
        origen = requerir_texto(fila, "origen")
        destino = requerir_texto(fila, "destino")
        if origen == destino:
            raise DatosInvalidosError("Una conexión no puede unir una ubicación consigo misma")
        return Conexion(origen, destino,
                        requerir_numero(fila, "distancia_km", True),
                        requerir_opcion(fila, "trafico", C.es_trafico, "BAJO, MEDIO, ALTO"),
                        requerir_numero(fila, "peaje", False))

    def invertida(self):
        return Conexion(self.destino, self.origen, self.distancia_km, self.trafico, self.peaje)

    def tiempo_min(self):
        return self.distancia_km / C.VELOCIDAD_BASE_KMH * 60.0 * C.factor_trafico(self.trafico)

    def costo(self):
        return self.distancia_km * C.COSTO_POR_KM + self.peaje

    def peso(self, criterio):
        if criterio == "DISTANCIA":
            return self.distancia_km
        if criterio == "TIEMPO":
            return self.tiempo_min()
        if criterio == "COSTO":
            return self.costo()
        raise DatosInvalidosError(f"Criterio desconocido: {criterio}")


@dataclass
class Vehiculo:
    id: str
    tipo: str
    capacidad: int
    estado: str = "DISPONIBLE"
    conductor: str = "Sin conductor"

    @staticmethod
    def desde_fila(fila):
        return Vehiculo(requerir_texto(fila, "id"), requerir_texto(fila, "tipo"),
                        requerir_entero(fila, "capacidad"),
                        requerir_opcion(fila, "estado", C.es_estado_vehiculo, "DISPONIBLE, OCUPADO"),
                        fila.obtener_opcional("conductor", "Sin conductor"))

    @property
    def disponible(self):
        return self.estado == "DISPONIBLE"

    def ocupar(self):
        self.estado = "OCUPADO"

    def liberar(self):
        self.estado = "DISPONIBLE"


@dataclass(frozen=True)
class Solicitud:
    id: str
    origen: str
    destino: str
    prioridad: str
    criterio: str
    pasajeros: int

    @staticmethod
    def desde_fila(fila):
        origen = requerir_texto(fila, "origen")
        destino = requerir_texto(fila, "destino")
        if origen == destino:
            raise DatosInvalidosError("Origen y destino de la solicitud deben ser distintos")
        return Solicitud(requerir_texto(fila, "id"), origen, destino,
                         requerir_opcion(fila, "prioridad", C.es_prioridad, "CRITICA, ALTA, MEDIA, BAJA"),
                         requerir_opcion(fila, "criterio", C.es_criterio, "DISTANCIA, TIEMPO, COSTO"),
                         requerir_entero(fila, "pasajeros"))