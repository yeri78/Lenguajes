package transporte;

import java.nio.file.Path;
import java.util.Comparator;
import java.util.Optional;

// Responsable: Integrante 4 (asignación, datos y CLI)

/** Lo que hace la ventana, sin dibujar nada (así se puede probar sin pantalla). */
public class VentanaLogica {
    /** Resultado de procesar solicitudes.csv: una fila de texto por solicitud y el resumen. */
    public record Procesado(ListaEnlazada<String[]> filas, String resumen) { }

    private final Path datos = Datos.raizProyecto().resolve("data");
    private final Red red = Datos.cargarRed(datos);
    private final ListaEnlazada<Vehiculo> vehiculos = Datos.cargarVehiculos(datos);
    private final Asignacion.GestorFlota flota = new Asignacion.GestorFlota(vehiculos);
    private ListaEnlazada<Ruta> rutas = new ListaEnlazada<>();
    private String origen;
    private String destino;
    private int contador = 0;

    public Red red() {
        return red;
    }

    public Asignacion.GestorFlota flota() {
        return flota;
    }

    public String nombre(String id) {
        return red.ubicaciones().buscar(u -> u.id().equals(id)).map(Ubicacion::nombre).orElse(id);
    }

    private String nombres(Ruta ruta) {
        return ruta.nodos().transformar(this::nombre).unir(" -> ");
    }

    /** Textos "L1 - Pachuca" para los desplegables. */
    public ListaEnlazada<String> etiquetasUbicaciones() {
        return red.ubicaciones().transformar(u -> u.id() + " - " + u.nombre());
    }

    public static String idDe(Object etiqueta) {
        return etiqueta == null ? "" : etiqueta.toString().split(" - ")[0].trim();
    }

    /** Busca las rutas, las ordena por tiempo y devuelve una fila de texto por ruta (vacía si no hay camino). */
    public ListaEnlazada<String[]> buscarRutas(String desde, String hasta) {
        if (desde.isEmpty() || hasta.isEmpty()) {
            throw new DatosInvalidosException("Elige origen y destino");
        }
        if (desde.equals(hasta)) {
            throw new DatosInvalidosException("Origen y destino deben ser distintos");
        }
        rutas = Rutas.todasLasRutas(red, desde, hasta).ordenada(Comparator.comparingDouble(Ruta::tiempoMin));
        origen = desde;
        destino = hasta;
        ListaEnlazada<String[]> filas = new ListaEnlazada<>();
        if (rutas.estaVacia()) {
            return filas;
        }
        String corta = Rutas.mejorRuta(red, desde, hasta, "DISTANCIA").texto();
        String rapida = Rutas.mejorRuta(red, desde, hasta, "TIEMPO").texto();
        String barata = Rutas.mejorRuta(red, desde, hasta, "COSTO").texto();
        int numero = 1;
        for (Ruta r : rutas) {
            String marcas = ((r.texto().equals(corta) ? " MAS CORTA" : "")
                    + (r.texto().equals(rapida) ? " MENOR TIEMPO" : "")
                    + (r.texto().equals(barata) ? " MENOR COSTO" : "")).trim();
            filas.agregarFinal(new String[]{String.valueOf(numero++), nombres(r), Datos.f2(r.distanciaKm()),
                    Interactivo.tiempo(r.tiempoMin()), "$" + Datos.f2(r.costo()), marcas});
        }
        return filas;
    }

    /** Crea la solicitud, asigna vehículo y devuelve el texto del resultado. */
    public String asignar(int numeroRuta, String cantidad, String prioridad) {
        if (rutas.estaVacia()) {
            throw new DatosInvalidosException("Primero busca rutas");
        }
        if (numeroRuta < 1 || numeroRuta > rutas.tamano()) {
            throw new DatosInvalidosException("Selecciona una ruta de la tabla");
        }
        Ruta ruta = rutas.obtener(numeroRuta - 1);
        Solicitud solicitud = Solicitud.desdeFila(Fila.de("id", "M" + (contador + 1), "origen", origen,
                "destino", destino, "criterio", "TIEMPO", "pasajeros", cantidad.trim(), "prioridad", prioridad));
        contador++;
        Optional<Vehiculo> vehiculo = flota.asignar(solicitud.pasajeros());
        if (vehiculo.isEmpty()) {
            return "No hay vehículo disponible para " + solicitud.pasajeros() + " pasajeros.";
        }
        return "Solicitud " + solicitud.id() + " ASIGNADA\n"
                + "  Vehículo:  " + vehiculo.get().id() + " (" + vehiculo.get().tipo() + ")\n"
                + "  Conductor: " + vehiculo.get().conductor() + "\n"
                + "  Ruta:      " + nombres(ruta) + "\n"
                + "  Tiempo estimado: " + Interactivo.tiempo(ruta.tiempoMin()) + " | Costo: $"
                + Datos.f2(ruta.costo()) + "\n"
                + "  Tiempo máximo de respuesta (" + solicitud.prioridad() + "): "
                + Constantes.horasMaxRespuesta(solicitud.prioridad()) + " h -> "
                + (Asignacion.cumpleSla(solicitud, ruta) ? "SI cumple" : "NO cumple");
    }

    public void finalizarViaje(String id) {
        Vehiculo vehiculo = vehiculos.buscar(v -> v.id().equals(id))
                .orElseThrow(() -> new DatosInvalidosException("Vehículo no registrado: " + id));
        vehiculo.liberar();
    }

    public void cambiarTrafico(String a, String b, String trafico) {
        red.cambiarTrafico(a, b, trafico);
    }

    /** Procesa solicitudes.csv con una flota nueva (no toca la flota de la pestaña Vehículos). */
    public Procesado procesarSolicitudes() {
        Red redNueva = Datos.cargarRed(datos);
        ListaEnlazada<Solicitud> solicitudes = Datos.cargarSolicitudes(datos, redNueva);
        Servicio.Salida salida = Servicio.procesar(redNueva, Datos.cargarVehiculos(datos), solicitudes, true);
        ListaEnlazada<String[]> filas = salida.resultados().transformar(r -> new String[]{
                r.solicitud().id(), r.solicitud().prioridad(), r.estado(), r.vehiculo(), r.cumpleSla(),
                r.ruta() != null ? r.ruta().texto() : "-"});
        return new Procesado(filas, salida.resumen().transformar(p -> p[0] + ": " + p[1]).unir("\n"));
    }
}
