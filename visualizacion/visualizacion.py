"""Genera visualizacion/index.html (autocontenido) con los resultados reales.

Uso (desde la raíz):  python visualizacion/generar_visualizacion.py
Lee data/*.csv y resultados/*.csv; si falta algún benchmark, se muestra vacío.
"""
import csv
import json
import os
import re

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LENGUAJES = {"python": ("python", "*.py"), "javascript": ("javascript", "*.js"), "java": ("java", "*.java")}
EXT = {"python": ".py", "javascript": ".js", "java": ".java"}
COMENTARIO = re.compile(r"^\s*(#|//|/\*|\*|\"\"\")")

# Estimación del equipo (editable): 1 = muy fácil, 5 = muy difícil.
DIFICULTAD = {
    "python": {"nota": 2, "motivo": "Sintaxis breve, dataclasses y ThreadPoolExecutor; el GIL limita el paralelismo real."},
    "javascript": {"nota": 3, "motivo": "Sin tipos ni PQ nativa; worker_threads exige serializar datos entre hilos."},
    "java": {"nota": 4, "motivo": "Más código (tipos, records, excepciones); concurrencia muy robusta con ExecutorService."},
}
PROS_CONTRAS = {
    "python": {"pros": ["Menos líneas y lectura muy clara", "Biblioteca estándar completa (csv, unittest, heapq)", "Ideal para prototipar y analizar datos"],
               "contras": ["Hilos limitados por el GIL en tareas de CPU", "Tipado dinámico: errores aparecen en ejecución", "Más lento en cómputo intensivo"]},
    "javascript": {"pros": ["Mismo lenguaje para web y servidor", "Modelo asíncrono y eventos muy natural", "Ejecutor de pruebas incluido en Node"],
                   "contras": ["Coerción implícita de tipos (tipado débil)", "Paralelismo real solo con worker_threads", "Sin cola de prioridad ni CSV nativos"]},
    "java": {"pros": ["Tipado estático detecta errores al compilar", "Concurrencia madura (ExecutorService, Futures)", "JIT: muy rápido con volúmenes grandes"],
             "contras": ["Código más extenso y ceremonioso", "Requiere JDK y paso de compilación", "Arranque en frío más lento (JVM)"]},
}


def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def contar_lineas(lenguaje):
    carpeta, _ = LENGUAJES[lenguaje]
    fuente = prueba = 0
    for base, dirs, archivos in os.walk(os.path.join(RAIZ, carpeta)):
        dirs[:] = [d for d in dirs if d not in ("out", "node_modules", "__pycache__")]
        for nombre in archivos:
            if not nombre.endswith(EXT[lenguaje]):
                continue
            with open(os.path.join(base, nombre), encoding="utf-8") as f:
                n = sum(1 for l in f if l.strip() and not COMENTARIO.match(l))
            if "test" in base.lower() or nombre.lower().startswith("pruebas"):
                prueba += n
            else:
                fuente += n
    return {"fuente": fuente, "pruebas": prueba}


def main():
    datos = {
        "ubicaciones": leer_csv(os.path.join(RAIZ, "data", "ubicaciones.csv")),
        "conexiones": leer_csv(os.path.join(RAIZ, "data", "conexiones.csv")),
        "resultados": {l: leer_csv(os.path.join(RAIZ, "resultados", f"resultados_{l}.csv")) for l in LENGUAJES},
        "resumen": {l: leer_csv(os.path.join(RAIZ, "resultados", f"resumen_{l}.csv")) for l in LENGUAJES},
        "benchmark": [f for l in LENGUAJES for f in leer_csv(os.path.join(RAIZ, "resultados", f"benchmark_{l}.csv"))],
        "lineas": {l: contar_lineas(l) for l in LENGUAJES},
        "dificultad": DIFICULTAD,
        "proscontras": PROS_CONTRAS,
    }
    with open(os.path.join(os.path.dirname(__file__), "plantilla.html"), encoding="utf-8") as f:
        plantilla = f.read()
    html = plantilla.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
    destino = os.path.join(os.path.dirname(__file__), "index.html")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generado: {destino}")


if __name__ == "__main__":
    main()
