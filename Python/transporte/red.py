# Responsable: Integrante 3 (red, rutas y estadísticas)
"""Red de transporte guardada en dos listas enlazadas: ubicaciones y conexiones.

Cada conexión se guarda una sola vez y se puede recorrer en ambos sentidos.
"""
from .constantes import es_trafico
from .lista_enlazada import ListaEnlazada
from .modelos import Conexion
from .validacion import DatosInvalidosError


class Red:
    def __init__(self):
        self._ubicaciones = ListaEnlazada()
        self._conexiones = ListaEnlazada()

    def registrar_ubicacion(self, ubicacion):
        if self.existe(ubicacion.id):
            raise DatosInvalidosError(f"Ubicación duplicada: {ubicacion.id}")
        self._ubicaciones.agregar_final(ubicacion)

    def registrar_conexion(self, conexion):
        self.validar_ubicacion(conexion.origen)
        self.validar_ubicacion(conexion.destino)
        if self.buscar_conexion(conexion.origen, conexion.destino) is not None:
            raise DatosInvalidosError(f"Conexión duplicada: {conexion.origen}-{conexion.destino}")
        self._conexiones.agregar_final(conexion)

    def existe(self, id_ubicacion):
        return self._ubicaciones.contiene(lambda u: u.id == id_ubicacion)

    def validar_ubicacion(self, id_ubicacion):
        if not self.existe(id_ubicacion):
            raise DatosInvalidosError(f"Ubicación desconocida: {id_ubicacion}")

    def buscar_conexion(self, a, b):
        """Conexión entre a y b orientada de a hacia b, o None si no existe."""
        for c in self._conexiones:
            if c.origen == a and c.destino == b:
                return c
            if c.origen == b and c.destino == a:
                return c.invertida()
        return None

    def vecinos(self, id_ubicacion):
        """Conexiones que salen de la ubicación, todas orientadas desde ella."""
        salientes = ListaEnlazada()
        for c in self._conexiones:
            if c.origen == id_ubicacion:
                salientes.agregar_final(c)
            elif c.destino == id_ubicacion:
                salientes.agregar_final(c.invertida())
        return salientes

    def cambiar_trafico(self, a, b, nuevo_trafico):
        """Cambia el nivel de tráfico de un tramo (en ambos sentidos)."""
        if not es_trafico(nuevo_trafico):
            raise DatosInvalidosError(f"Tráfico inválido: {nuevo_trafico}. Opciones: BAJO, MEDIO, ALTO")
        if self.buscar_conexion(a, b) is None:
            raise DatosInvalidosError(f"No existe conexión entre {a} y {b}")

        def une(c):
            return (c.origen == a and c.destino == b) or (c.origen == b and c.destino == a)

        self._conexiones = self._conexiones.transformar(
            lambda c: Conexion(c.origen, c.destino, c.distancia_km, nuevo_trafico, c.peaje) if une(c) else c)

    def ubicaciones(self):
        return self._ubicaciones

    def conexiones(self):
        return self._conexiones