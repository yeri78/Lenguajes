# Responsable: Integrante 4 (asignación, datos y CLI)
"""Ventana gráfica (tkinter) del sistema de transporte.

Se abre con:  python main.py ventana
Usa las mismas listas enlazadas y reglas que el resto del programa; la ventana solo muestra y pide datos.
"""
from .asignacion import GestorFlota, cumple_sla
from .constantes import horas_max_respuesta
from .datos import cargar_red, cargar_solicitudes, cargar_vehiculos, f2, raiz_proyecto
from .fila import Fila
from .interactivo import tiempo
from .lista_enlazada import ListaEnlazada
from .modelos import Solicitud
from .rutas import mejor_ruta, todas_las_rutas
from .servicio import procesar
from .validacion import DatosInvalidosError

PRIORIDADES = ("CRITICA", "ALTA", "MEDIA", "BAJA")
TRAFICOS = ("BAJO", "MEDIO", "ALTO")


class LogicaVentana:
    """Lo que hace la ventana, sin dibujar nada (así se puede probar sin pantalla)."""

    def __init__(self):
        self.carpeta = raiz_proyecto() / "data"
        self.red = cargar_red(self.carpeta)
        self.vehiculos = cargar_vehiculos(self.carpeta)
        self.flota = GestorFlota(self.vehiculos)
        self.rutas = None          # ListaEnlazada de Ruta, de la última búsqueda
        self.origen = None
        self.destino = None
        self.contador = 0

    def nombre(self, id_ubicacion):
        ubicacion = self.red.ubicaciones().buscar(lambda u: u.id == id_ubicacion)
        return ubicacion.nombre if ubicacion else id_ubicacion

    def nombres(self, ruta):
        return ruta.nodos.transformar(self.nombre).unir(" -> ")

    def etiquetas_ubicaciones(self):
        """Lista enlazada de textos 'L1 - Pachuca' para los desplegables."""
        return self.red.ubicaciones().transformar(lambda u: f"{u.id} - {u.nombre}")

    @staticmethod
    def id_de(etiqueta):
        return etiqueta.split(" - ")[0].strip()

    def buscar_rutas(self, origen, destino):
        """Devuelve lista enlazada de (numero, ruta, texto_nombres, marcas) ordenada por tiempo."""
        if not origen or not destino:
            raise DatosInvalidosError("Elige origen y destino")
        if origen == destino:
            raise DatosInvalidosError("Origen y destino deben ser distintos")
        rutas = todas_las_rutas(self.red, origen, destino).ordenada(
            lambda a, b: -1 if a.tiempo_min < b.tiempo_min else (1 if a.tiempo_min > b.tiempo_min else 0))
        self.rutas, self.origen, self.destino = rutas, origen, destino
        if rutas.esta_vacia():
            return rutas
        corta = mejor_ruta(self.red, origen, destino, "DISTANCIA").texto()
        rapida = mejor_ruta(self.red, origen, destino, "TIEMPO").texto()
        barata = mejor_ruta(self.red, origen, destino, "COSTO").texto()
        filas = ListaEnlazada()
        numero = 0
        for r in rutas:
            numero += 1
            marcas = ((" MAS CORTA" if r.texto() == corta else "")
                      + (" MENOR TIEMPO" if r.texto() == rapida else "")
                      + (" MENOR COSTO" if r.texto() == barata else "")).strip()
            filas.agregar_final((numero, r, self.nombres(r), marcas))
        return filas

    def asignar(self, numero_ruta, pasajeros, prioridad):
        """Crea la solicitud, asigna vehículo y devuelve el texto del resultado."""
        if self.rutas is None or self.rutas.esta_vacia():
            raise DatosInvalidosError("Primero busca rutas")
        if numero_ruta < 1 or numero_ruta > self.rutas.tamano():
            raise DatosInvalidosError("Selecciona una ruta de la tabla")
        ruta = self.rutas.obtener(numero_ruta - 1)
        solicitud = Solicitud.desde_fila(Fila.de(
            "id", f"M{self.contador + 1}", "origen", self.origen, "destino", self.destino,
            "criterio", "TIEMPO", "pasajeros", str(pasajeros).strip(), "prioridad", prioridad))
        self.contador += 1
        vehiculo = self.flota.asignar(solicitud.pasajeros)
        if vehiculo is None:
            return f"No hay vehículo disponible para {solicitud.pasajeros} pasajeros."
        return (f"Solicitud {solicitud.id} ASIGNADA\n"
                f"  Vehículo:  {vehiculo.id} ({vehiculo.tipo})\n"
                f"  Conductor: {vehiculo.conductor}\n"
                f"  Ruta:      {self.nombres(ruta)}\n"
                f"  Tiempo estimado: {tiempo(ruta.tiempo_min)} | Costo: ${f2(ruta.costo)}\n"
                f"  Tiempo máximo de respuesta ({solicitud.prioridad}): {horas_max_respuesta(solicitud.prioridad)} h -> "
                f"{'SI cumple' if cumple_sla(solicitud, ruta) else 'NO cumple'}")

    def finalizar_viaje(self, id_vehiculo):
        vehiculo = self.vehiculos.buscar(lambda v: v.id == id_vehiculo)
        if vehiculo is None:
            raise DatosInvalidosError(f"Vehículo no registrado: {id_vehiculo}")
        vehiculo.liberar()

    def cambiar_trafico(self, a, b, trafico):
        self.red.cambiar_trafico(a, b, trafico)

    def procesar_solicitudes(self):
        """Procesa solicitudes.csv con una flota nueva (no toca la flota de la pestaña Vehículos)."""
        red = cargar_red(self.carpeta)
        solicitudes = cargar_solicitudes(self.carpeta, red)
        resultados, resumen, _ = procesar(red, cargar_vehiculos(self.carpeta), solicitudes, concurrente=True)
        return resultados, resumen


def abrir():
    """Crea y muestra la ventana (bloquea hasta que se cierra)."""
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError:
        print("Este Python no trae tkinter. En Windows/macOS reinstala Python desde python.org;"
              " en Linux: sudo apt install python3-tk")
        return 1

    try:
        logica = LogicaVentana()
    except DatosInvalidosError as error:
        print(f"Error de datos: {error}")
        return 2

    raiz = tk.Tk()
    raiz.title("Sistema de transporte (Python)")
    raiz.geometry("980x640")
    raiz.minsize(820, 540)

    def error(e):
        messagebox.showwarning("Dato inválido", str(e), parent=raiz)

    def tabla(padre, columnas, anchos, alto=8):
        marco = ttk.Frame(padre)
        arbol = ttk.Treeview(marco, columns=[c for c, _ in columnas], show="headings", height=alto)
        for (clave, titulo), ancho in zip(columnas, anchos):
            arbol.heading(clave, text=titulo)
            arbol.column(clave, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=arbol.yview)
        arbol.configure(yscrollcommand=barra.set)
        arbol.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return marco, arbol

    def vaciar(arbol):
        arbol.delete(*arbol.get_children())

    cuaderno = ttk.Notebook(raiz)
    cuaderno.pack(fill="both", expand=True, padx=8, pady=8)

    # ---------------- Pestaña 1: viaje ----------------
    p1 = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(p1, text="Consultar y asignar viaje")
    etiquetas = tuple(logica.etiquetas_ubicaciones())
    fila1 = ttk.Frame(p1)
    fila1.pack(fill="x")
    ttk.Label(fila1, text="Origen:").pack(side="left")
    combo_origen = ttk.Combobox(fila1, values=etiquetas, state="readonly", width=22)
    combo_origen.pack(side="left", padx=(4, 12))
    ttk.Label(fila1, text="Destino:").pack(side="left")
    combo_destino = ttk.Combobox(fila1, values=etiquetas, state="readonly", width=22)
    combo_destino.pack(side="left", padx=(4, 12))
    marco_rutas, arbol_rutas = tabla(
        p1, (("n", "N°"), ("ruta", "Ruta"), ("km", "Km"), ("tiempo", "Tiempo"), ("costo", "Costo"), ("marcas", "Destaca")),
        (40, 420, 70, 90, 80, 230), alto=9)
    resultado_viaje = tk.Text(p1, height=8, state="disabled", wrap="word")

    def mostrar_viaje(texto):
        resultado_viaje.configure(state="normal")
        resultado_viaje.delete("1.0", "end")
        resultado_viaje.insert("1.0", texto)
        resultado_viaje.configure(state="disabled")

    def buscar():
        vaciar(arbol_rutas)
        mostrar_viaje("")
        try:
            filas = logica.buscar_rutas(logica.id_de(combo_origen.get()), logica.id_de(combo_destino.get()))
        except DatosInvalidosError as e:
            error(e)
            return
        if filas.esta_vacia():
            mostrar_viaje("No hay ruta entre esas dos ubicaciones.")
            return
        for numero, r, texto, marcas in filas:
            arbol_rutas.insert("", "end", iid=str(numero), values=(
                numero, texto, f2(r.distancia_km), tiempo(r.tiempo_min), "$" + f2(r.costo), marcas))
        mostrar_viaje("Elige una ruta de la tabla, escribe pasajeros y prioridad, y pulsa «Asignar viaje».")

    ttk.Button(fila1, text="Buscar rutas", command=buscar).pack(side="left")
    marco_rutas.pack(fill="both", expand=True, pady=8)

    fila2 = ttk.Frame(p1)
    fila2.pack(fill="x")
    ttk.Label(fila2, text="Pasajeros:").pack(side="left")
    pasajeros = ttk.Spinbox(fila2, from_=1, to=100, width=6)
    pasajeros.set("1")
    pasajeros.pack(side="left", padx=(4, 12))
    ttk.Label(fila2, text="Prioridad:").pack(side="left")
    prioridad = ttk.Combobox(fila2, values=PRIORIDADES, state="readonly", width=10)
    prioridad.set("MEDIA")
    prioridad.pack(side="left", padx=(4, 12))

    def asignar():
        seleccion = arbol_rutas.selection()
        if not seleccion:
            error(DatosInvalidosError("Selecciona una ruta de la tabla"))
            return
        try:
            mostrar_viaje(logica.asignar(int(seleccion[0]), pasajeros.get(), prioridad.get()))
        except DatosInvalidosError as e:
            error(e)
            return
        refrescar_vehiculos()

    ttk.Button(fila2, text="Asignar viaje", command=asignar).pack(side="left")
    resultado_viaje.pack(fill="x", pady=(8, 0))

    # ---------------- Pestaña 2: vehículos ----------------
    p2 = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(p2, text="Vehículos")
    columnas_v = (("id", "Id"), ("tipo", "Tipo"), ("cap", "Cap."), ("conductor", "Conductor"))
    anchos_v = (50, 100, 50, 160)
    izq = ttk.LabelFrame(p2, text="Disponibles", padding=6)
    izq.pack(side="left", fill="both", expand=True, padx=(0, 6))
    marco_d, arbol_disp = tabla(izq, columnas_v, anchos_v, alto=14)
    marco_d.pack(fill="both", expand=True)
    der = ttk.LabelFrame(p2, text="Ocupados", padding=6)
    der.pack(side="left", fill="both", expand=True)
    marco_o, arbol_ocup = tabla(der, columnas_v, anchos_v, alto=14)
    marco_o.pack(fill="both", expand=True)

    def refrescar_vehiculos():
        vaciar(arbol_disp)
        vaciar(arbol_ocup)
        logica.flota.disponibles().para_cada(lambda v: arbol_disp.insert(
            "", "end", iid=v.id, values=(v.id, v.tipo, v.capacidad, v.conductor)))
        logica.flota.ocupados().para_cada(lambda v: arbol_ocup.insert(
            "", "end", iid=v.id, values=(v.id, v.tipo, v.capacidad, v.conductor)))

    def finalizar():
        seleccion = arbol_ocup.selection()
        if not seleccion:
            error(DatosInvalidosError("Selecciona un vehículo en la lista de ocupados"))
            return
        try:
            logica.finalizar_viaje(seleccion[0])
        except DatosInvalidosError as e:
            error(e)
            return
        refrescar_vehiculos()

    ttk.Button(izq, text="Actualizar", command=refrescar_vehiculos).pack(pady=(6, 0))
    ttk.Button(der, text="Finalizar viaje del seleccionado", command=finalizar).pack(pady=(6, 0))
    refrescar_vehiculos()

    # ---------------- Pestaña 3: red y tráfico ----------------
    p3 = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(p3, text="Red y tráfico")
    marco_c, arbol_con = tabla(
        p3, (("a", "Desde"), ("b", "Hasta"), ("km", "Km"), ("trafico", "Tráfico"), ("peaje", "Peaje")),
        (200, 200, 80, 100, 80), alto=14)
    marco_c.pack(fill="both", expand=True)

    def refrescar_red():
        vaciar(arbol_con)
        logica.red.conexiones().para_cada(lambda c: arbol_con.insert(
            "", "end", iid=f"{c.origen}|{c.destino}",
            values=(logica.nombre(c.origen), logica.nombre(c.destino), f"{c.distancia_km:.1f}", c.trafico,
                    "$" + f2(c.peaje))))

    fila3 = ttk.Frame(p3)
    fila3.pack(fill="x", pady=(8, 0))
    ttk.Label(fila3, text="Nuevo tráfico del tramo seleccionado:").pack(side="left")
    combo_trafico = ttk.Combobox(fila3, values=TRAFICOS, state="readonly", width=8)
    combo_trafico.set("ALTO")
    combo_trafico.pack(side="left", padx=8)

    def aplicar_trafico():
        seleccion = arbol_con.selection()
        if not seleccion:
            error(DatosInvalidosError("Selecciona un tramo de la tabla"))
            return
        a, b = seleccion[0].split("|")
        try:
            logica.cambiar_trafico(a, b, combo_trafico.get())
        except DatosInvalidosError as e:
            error(e)
            return
        refrescar_red()

    ttk.Button(fila3, text="Aplicar", command=aplicar_trafico).pack(side="left")
    ttk.Label(fila3, text="(luego vuelve a «Buscar rutas» para ver el efecto)").pack(side="left", padx=10)
    refrescar_red()

    # ---------------- Pestaña 4: procesar solicitudes ----------------
    p4 = ttk.Frame(cuaderno, padding=10)
    cuaderno.add(p4, text="Procesar solicitudes")
    marco_s, arbol_sol = tabla(
        p4, (("id", "Solicitud"), ("prio", "Prioridad"), ("estado", "Estado"), ("veh", "Vehículo"),
             ("sla", "Cumple SLA"), ("ruta", "Ruta")),
        (80, 90, 90, 70, 80, 400), alto=11)
    resumen_texto = tk.Text(p4, height=7, state="disabled")

    def procesar_todo():
        vaciar(arbol_sol)
        try:
            resultados, resumen = logica.procesar_solicitudes()
        except DatosInvalidosError as e:
            error(e)
            return
        resultados.para_cada(lambda r: arbol_sol.insert("", "end", values=(
            r.solicitud.id, r.solicitud.prioridad, r.estado, r.vehiculo, r.cumple_sla,
            r.ruta.texto() if r.ruta else "-")))
        resumen_texto.configure(state="normal")
        resumen_texto.delete("1.0", "end")
        resumen_texto.insert("1.0", resumen.transformar(lambda par: f"{par[0]}: {par[1]}").unir("\n"))
        resumen_texto.configure(state="disabled")

    ttk.Button(p4, text="Procesar todas las solicitudes (en paralelo)", command=procesar_todo).pack(anchor="w")
    marco_s.pack(fill="both", expand=True, pady=8)
    resumen_texto.pack(fill="x")

    raiz.mainloop()
    return 0
