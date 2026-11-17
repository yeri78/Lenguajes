# Responsable: Integrante 4 (asignación, datos y CLI)
"""Modo interactivo sencillo: ver rutas, elegir una y asignar vehículo y conductor."""
import math

from .asignacion import GestorFlota, cumple_sla
from .constantes import horas_max_respuesta
from .datos import f2
from .fila import Fila
from .modelos import Solicitud
from .rutas import mejor_ruta, todas_las_rutas
from .validacion import DatosInvalidosError


def tiempo(minutos):
    total = int(math.floor(minutos + 0.5))   # redondeo "half up", igual que Java y JavaScript
    return f"{total // 60} h {total % 60} min" if total >= 60 else f"{total} min"


class Interactivo:
    def __init__(self, red, vehiculos):
        self.red = red
        self.vehiculos = vehiculos
        self.flota = GestorFlota(vehiculos)
        self.contador = 0

    def _leer(self, mensaje):
        """Lee una línea; si ya no hay entrada devuelve '0' para salir."""
        try:
            return input(mensaje).strip()
        except EOFError:
            return "0"

    def _nombre(self, id_ubicacion):
        ubicacion = self.red.ubicaciones().buscar(lambda u: u.id == id_ubicacion)
        return ubicacion.nombre if ubicacion else id_ubicacion

    def _nombres(self, ruta):
        return ruta.nodos.transformar(self._nombre).unir(" -> ")

    def _resolver(self, texto):
        """Acepta el id (L1) o el nombre (Pachuca) y devuelve el id."""
        t = texto.lower()
        ubicacion = self.red.ubicaciones().buscar(lambda u: u.id.lower() == t or u.nombre.lower() == t)
        if ubicacion is None:
            raise DatosInvalidosError(f"Ubicación desconocida: {texto}")
        return ubicacion.id

    def ejecutar(self):
        opcion = ""
        while opcion != "0":
            print("\n1) Ver red   2) Consultar rutas y asignar viaje   3) Ver vehículos")
            print("4) Finalizar viaje   5) Cambiar tráfico de un tramo   0) Salir")
            opcion = self._leer("Elige una opción: ")
            try:
                if opcion == "1":
                    self._ver_red()
                elif opcion == "2":
                    self._consultar_y_asignar()
                elif opcion == "3":
                    self._ver_vehiculos()
                elif opcion == "4":
                    self._finalizar_viaje()
                elif opcion == "5":
                    self._cambiar_trafico()
                elif opcion == "0":
                    print("Hasta luego.")
                else:
                    print("Opción no válida.")
            except DatosInvalidosError as error:
                print(f"Dato inválido: {error}")

    def _ver_red(self):
        print("Ubicaciones:")
        self.red.ubicaciones().para_cada(lambda u: print(f"  {u.id} {u.nombre}"))
        print("Conexiones:")
        self.red.conexiones().para_cada(lambda c: print(
            f"  {self._nombre(c.origen)} <-> {self._nombre(c.destino)}  {c.distancia_km:.1f} km  "
            f"tráfico {c.trafico}  peaje ${c.peaje:.1f}"))

    def _ver_vehiculos(self):
        def mostrar(v):
            print(f"  {v.id} {v.tipo} (cap. {v.capacidad}) conductor: {v.conductor}")

        print("Disponibles:")
        self.flota.disponibles().para_cada(mostrar)
        print("Ocupados:")
        self.flota.ocupados().para_cada(mostrar)

    def _consultar_y_asignar(self):
        print("Ubicaciones: " + self.red.ubicaciones().transformar(lambda u: u.nombre).unir(", "))
        origen = self._resolver(self._leer("Origen (nombre o id): "))
        destino = self._resolver(self._leer("Destino (nombre o id): "))
        if origen == destino:
            raise DatosInvalidosError("Origen y destino deben ser distintos")

        rutas = todas_las_rutas(self.red, origen, destino).ordenada(
            lambda a, b: -1 if a.tiempo_min < b.tiempo_min else (1 if a.tiempo_min > b.tiempo_min else 0))
        if rutas.esta_vacia():
            print(f"No hay ruta entre {self._nombre(origen)} y {self._nombre(destino)}")
            return
        corta = mejor_ruta(self.red, origen, destino, "DISTANCIA").texto()
        rapida = mejor_ruta(self.red, origen, destino, "TIEMPO").texto()
        barata = mejor_ruta(self.red, origen, destino, "COSTO").texto()

        print("Rutas disponibles (de menor a mayor tiempo, con tráfico incluido):")
        for numero, r in enumerate(rutas, start=1):
            marcas = ((" [MAS CORTA]" if r.texto() == corta else "")
                      + (" [MENOR TIEMPO]" if r.texto() == rapida else "")
                      + (" [MENOR COSTO]" if r.texto() == barata else ""))
            print(f"  {numero}) {self._nombres(r)} | {f2(r.distancia_km)} km | {tiempo(r.tiempo_min)} | ${f2(r.costo)}{marcas}")

        try:
            eleccion = int(self._leer("Número de ruta (0 = cancelar): "))
        except ValueError:
            raise DatosInvalidosError("Debes escribir un número válido")
        if eleccion == 0:
            return
        if eleccion < 1 or eleccion > rutas.tamano():
            raise DatosInvalidosError("Número de ruta fuera de rango")
        ruta = rutas.obtener(eleccion - 1)

        pasajeros = self._leer("Pasajeros: ")
        prioridad = self._leer("Prioridad (CRITICA/ALTA/MEDIA/BAJA): ").upper()
        self.contador += 1
        solicitud = Solicitud.desde_fila(Fila.de(
            "id", f"M{self.contador}", "origen", origen, "destino", destino,
            "criterio", "TIEMPO", "pasajeros", pasajeros, "prioridad", prioridad))

        vehiculo = self.flota.asignar(solicitud.pasajeros)
        if vehiculo is None:
            print(f"No hay vehículo disponible para {solicitud.pasajeros} pasajeros.")
            return
        print(f"\nSolicitud {solicitud.id} ASIGNADA")
        print(f"  Vehículo:  {vehiculo.id} ({vehiculo.tipo})")
        print(f"  Conductor: {vehiculo.conductor}")
        print(f"  Ruta:      {self._nombres(ruta)}")
        print(f"  Tiempo estimado: {tiempo(ruta.tiempo_min)} | Costo: ${f2(ruta.costo)}")
        print(f"  Tiempo máximo de respuesta ({solicitud.prioridad}): {horas_max_respuesta(solicitud.prioridad)} h -> "
              f"{'SI cumple' if cumple_sla(solicitud, ruta) else 'NO cumple'}")

    def _finalizar_viaje(self):
        id_vehiculo = self._leer("Id del vehículo que terminó (ej. V1): ").upper()
        vehiculo = self.vehiculos.buscar(lambda v: v.id == id_vehiculo)
        if vehiculo is None:
            raise DatosInvalidosError(f"Vehículo no registrado: {id_vehiculo}")
        vehiculo.liberar()
        print(f"Vehículo {id_vehiculo} disponible de nuevo.")

    def _cambiar_trafico(self):
        a = self._resolver(self._leer("Ubicación A (nombre o id): "))
        b = self._resolver(self._leer("Ubicación B (nombre o id): "))
        trafico = self._leer("Nuevo tráfico (BAJO/MEDIO/ALTO): ").upper()
        self.red.cambiar_trafico(a, b, trafico)
        print("Listo. Consulta rutas de nuevo para ver el efecto.")
