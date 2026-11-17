# Responsable: Integrante 4 (asignación, datos y CLI)
"""Lectura de CSV, construcción de la red y escritura de resultados."""
import os
from pathlib import Path

from .fila import Fila
from .lista_enlazada import ListaEnlazada
from .modelos import Conexion, Solicitud, Ubicacion, Vehiculo
from .red import Red
from .validacion import DatosInvalidosError


def raiz_proyecto():
    """Busca hacia arriba la carpeta que contiene data/ubicaciones.csv (funciona desde cualquier subcarpeta)."""
    for inicio in (Path.cwd(), Path(__file__).resolve().parent):
        carpeta = inicio
        for _ in range(6):
            if (carpeta / "data" / "ubicaciones.csv").exists():
                return carpeta
            if carpeta.parent == carpeta:
                break
            carpeta = carpeta.parent
    raise DatosInvalidosError("No se encontró la carpeta data con los CSV. Ejecuta desde la carpeta del proyecto.")


def leer_csv(ruta):
    try:
        with open(ruta, encoding="utf-8-sig") as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        raise DatosInvalidosError(f"No se encontró el archivo: {ruta}")
    lineas = ListaEnlazada.desde_iterable(contenido.splitlines()).filtrar(lambda l: l.strip() != "")
    if lineas.esta_vacia():
        raise DatosInvalidosError(f"Archivo vacío: {ruta}")
    encabezado = lineas.obtener(0)
    filas = ListaEnlazada()
    primera = True
    for linea in lineas:
        if primera:
            primera = False
        else:
            filas.agregar_final(Fila.desde_texto(encabezado, linea))
    return filas


def cargar_red(carpeta):
    red = Red()
    leer_csv(os.path.join(carpeta, "ubicaciones.csv")).para_cada(lambda f: red.registrar_ubicacion(Ubicacion.desde_fila(f)))
    leer_csv(os.path.join(carpeta, "conexiones.csv")).para_cada(lambda f: red.registrar_conexion(Conexion.desde_fila(f)))
    return red


def cargar_vehiculos(carpeta):
    return leer_csv(os.path.join(carpeta, "vehiculos.csv")).transformar(Vehiculo.desde_fila)


def cargar_solicitudes(carpeta, red):
    solicitudes = leer_csv(os.path.join(carpeta, "solicitudes.csv")).transformar(Solicitud.desde_fila)
    for s in solicitudes:
        red.validar_ubicacion(s.origen)
        red.validar_ubicacion(s.destino)
    return solicitudes


def f2(numero):
    return f"{numero:.2f}"


def escribir_lineas(archivo, encabezado, lineas):
    """Escribe un CSV: encabezado y una línea de texto por elemento de la lista."""
    os.makedirs(os.path.dirname(os.path.abspath(archivo)), exist_ok=True)
    with open(archivo, "w", encoding="utf-8", newline="\n") as salida:
        salida.write(encabezado + "\n")
        for linea in lineas:
            salida.write(linea + "\n")


def escribir_resultados(archivo, resultados):
    def a_linea(r):
        ruta = r.ruta
        return ",".join((r.solicitud.id, r.solicitud.prioridad, r.solicitud.criterio, r.estado, r.vehiculo,
                         ruta.texto() if ruta else "-", f2(ruta.distancia_km) if ruta else "-",
                         f2(ruta.tiempo_min) if ruta else "-", f2(ruta.costo) if ruta else "-", r.cumple_sla))

    escribir_lineas(archivo, "solicitud,prioridad,criterio,estado,vehiculo,ruta,distancia_km,tiempo_min,costo,cumple_sla",
                    resultados.transformar(a_linea))


def escribir_resumen(archivo, resumen):
    escribir_lineas(archivo, "metrica,valor", resumen.transformar(lambda par: f"{par[0]},{par[1]}"))
