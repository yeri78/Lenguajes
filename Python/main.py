# Responsable: Integrante 4 (asignación, datos y CLI)
"""Interfaz de línea de comandos.

Uso:
  python main.py procesar
  python main.py consultar ORIGEN DESTINO
  python main.py vehiculos
  python main.py red
  python main.py benchmark
  python main.py interactivo
"""
import os
import sys
import time

from transporte.concurrencia import Pedido, calcular_rutas
from transporte.constantes import criterios
from transporte.datos import (cargar_red, cargar_solicitudes, cargar_vehiculos, escribir_lineas,
                              escribir_resultados, escribir_resumen, f2, raiz_proyecto)
from transporte.interactivo import Interactivo
from transporte.lista_enlazada import ListaEnlazada
from transporte.rutas import mejor_ruta, todas_las_rutas
from transporte.servicio import procesar
from transporte.validacion import DatosInvalidosError


def carpeta_datos():
    return os.path.join(raiz_proyecto(), "data")


def carpeta_salida():
    return os.path.join(raiz_proyecto(), "resultados")


def pedidos_sinteticos(red, n):
    ids = red.ubicaciones().transformar(lambda u: u.id).ordenada(lambda a, b: -1 if a < b else (1 if a > b else 0))
    tipos = criterios()
    pedidos = ListaEnlazada()
    for i in range(n):
        origen = ids.obtener((i * 7) % ids.tamano())
        destino = ids.obtener((i * 3 + 1) % ids.tamano())
        if origen == destino:
            destino = ids.obtener((i * 3 + 2) % ids.tamano())
        pedidos.agregar_final(Pedido(origen, destino, tipos.obtener(i % 3)))
    return pedidos


def cmd_procesar():
    red = cargar_red(carpeta_datos())
    solicitudes = cargar_solicitudes(carpeta_datos(), red)
    resultados, resumen, _ = procesar(red, cargar_vehiculos(carpeta_datos()), solicitudes, concurrente=True)
    resultados.para_cada(lambda r: print(
        f"{r.solicitud.id} {r.solicitud.prioridad:<8} {r.estado:<9} {r.vehiculo:<3} {r.ruta.texto() if r.ruta else '-'}"))
    print("\nResumen:")
    resumen.para_cada(lambda par: print(f"  {par[0]}: {par[1]}"))
    escribir_resultados(os.path.join(carpeta_salida(), "resultados_python.csv"), resultados)
    escribir_resumen(os.path.join(carpeta_salida(), "resumen_python.csv"), resumen)


def cmd_consultar(origen=None, destino=None):
    if not origen or not destino:
        raise DatosInvalidosError("Uso: python main.py consultar ORIGEN DESTINO")
    red = cargar_red(carpeta_datos())
    print(f"Rutas posibles {origen} -> {destino}:")
    todas_las_rutas(red, origen, destino).para_cada(lambda r: print(
        f"  {r.texto()}  {f2(r.distancia_km)} km  {f2(r.tiempo_min)} min  ${f2(r.costo)}"))
    for criterio in criterios():
        mejor = mejor_ruta(red, origen, destino, criterio)
        print(f"Mejor por {criterio}: {mejor.texto() if mejor else 'sin ruta'}")


def cmd_vehiculos():
    vehiculos = cargar_vehiculos(carpeta_datos())
    for estado in ("DISPONIBLE", "OCUPADO"):
        print(f"{estado}: {vehiculos.filtrar(lambda v: v.estado == estado).transformar(lambda v: v.id)}")


def cmd_red():
    red = cargar_red(carpeta_datos())
    print("Ubicaciones:")
    red.ubicaciones().para_cada(lambda u: print(f"  {u.id:<4} {u.nombre}"))
    print("Conexiones:")
    red.conexiones().para_cada(lambda c: print(
        f"  {c.origen:<4} <-> {c.destino:<4} {c.distancia_km:6.1f} km  tráfico {c.trafico:<5} peaje ${f2(c.peaje)}"))


def cmd_benchmark():
    red = cargar_red(carpeta_datos())
    filas = ListaEnlazada()
    for n in (100, 1000, 5000):
        pedidos = pedidos_sinteticos(red, n)
        inicio = time.perf_counter()
        calcular_rutas(red, pedidos, False)
        secuencial = (time.perf_counter() - inicio) * 1000
        inicio = time.perf_counter()
        calcular_rutas(red, pedidos, True)
        concurrente = (time.perf_counter() - inicio) * 1000
        filas.agregar_final(f"python,{n},{secuencial:.1f},{concurrente:.1f}")
        print(f"n={n}: secuencial={secuencial:.1f} ms, concurrente={concurrente:.1f} ms")
    escribir_lineas(os.path.join(carpeta_salida(), "benchmark_python.csv"),
                    "lenguaje,n,secuencial_ms,concurrente_ms", filas)


def cmd_interactivo():
    Interactivo(cargar_red(carpeta_datos()), cargar_vehiculos(carpeta_datos())).ejecutar()


def main(argumentos):
    comando = argumentos[0] if argumentos else ""
    try:
        if comando == "procesar":
            cmd_procesar()
        elif comando == "consultar":
            cmd_consultar(*argumentos[1:])
        elif comando == "vehiculos":
            cmd_vehiculos()
        elif comando == "red":
            cmd_red()
        elif comando == "benchmark":
            cmd_benchmark()
        elif comando == "interactivo":
            cmd_interactivo()
        else:
            print(__doc__)
            return 1
    except DatosInvalidosError as error:
        print(f"Error de datos: {error}", file=sys.stderr)
        return 2
    except TypeError:
        print("Argumentos incorrectos.\n" + __doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
