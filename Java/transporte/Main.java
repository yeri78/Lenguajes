package transporte;

import java.nio.file.Path;
import java.util.Comparator;
import java.util.Locale;

// Responsable: Integrante 4 (asignación, datos y CLI)

/** CLI: procesar | consultar ORIGEN DESTINO | vehiculos | red | benchmark. */
public final class Main {
    private static final Path RAIZ = Datos.raizProyecto();
    private static final Path DATOS = RAIZ.resolve("data");
    private static final Path SALIDA = RAIZ.resolve("resultados");
    private static final String USO =
            "Uso: java -cp out transporte.Main procesar | consultar ORIGEN DESTINO | vehiculos | red | benchmark";

    private Main() { }

    static ListaEnlazada<Concurrencia.Pedido> pedidosSinteticos(Red red, int n) {
        ListaEnlazada<String> ids = red.ubicaciones().transformar(Ubicacion::id).ordenada(Comparator.naturalOrder());
        String[] criterios = {"DISTANCIA", "TIEMPO", "COSTO"};
        ListaEnlazada<Concurrencia.Pedido> pedidos = new ListaEnlazada<>();
        for (int i = 0; i < n; i++) {
            String origen = ids.obtener((i * 7) % ids.tamano());
            String destino = ids.obtener((i * 3 + 1) % ids.tamano());
            if (origen.equals(destino)) {
                destino = ids.obtener((i * 3 + 2) % ids.tamano());
            }
            pedidos.agregarFinal(new Concurrencia.Pedido(origen, destino, criterios[i % 3]));
        }
        return pedidos;
    }

    static void procesar() {
        Red red = Datos.cargarRed(DATOS);
        ListaEnlazada<Solicitud> solicitudes = Datos.cargarSolicitudes(DATOS, red);
        Servicio.Salida salida = Servicio.procesar(red, Datos.cargarVehiculos(DATOS), solicitudes, true);
        for (ResultadoSolicitud r : salida.resultados()) {
            System.out.printf("%s %-8s %-9s %-3s %s%n", r.solicitud().id(), r.solicitud().prioridad(),
                    r.estado(), r.vehiculo(), r.ruta() != null ? r.ruta().texto() : "-");
        }
        System.out.println("\nResumen:");
        salida.resumen().forEach(p -> System.out.println("  " + p[0] + ": " + p[1]));
        Datos.escribirResultados(SALIDA.resolve("resultados_java.csv"), salida.resultados());
        Datos.escribirPares(SALIDA.resolve("resumen_java.csv"), "metrica,valor", salida.resumen());
    }

    static void consultar(String origen, String destino) {
        Red red = Datos.cargarRed(DATOS);
        System.out.println("Rutas posibles " + origen + " -> " + destino + ":");
        for (Ruta r : Rutas.todasLasRutas(red, origen, destino)) {
            System.out.println("  " + r.texto() + "  " + Datos.f2(r.distanciaKm()) + " km  "
                    + Datos.f2(r.tiempoMin()) + " min  $" + Datos.f2(r.costo()));
        }
        for (String criterio : Constantes.criterios()) {
            Ruta mejor = Rutas.mejorRuta(red, origen, destino, criterio);
            System.out.println("Mejor por " + criterio + ": " + (mejor != null ? mejor.texto() : "sin ruta"));
        }
    }

    static void vehiculos() {
        ListaEnlazada<Vehiculo> lista = Datos.cargarVehiculos(DATOS);
        for (String estado : new String[]{"DISPONIBLE", "OCUPADO"}) {
            System.out.println(estado + ": " + lista.filtrar(v -> v.estado().equals(estado)).transformar(Vehiculo::id));
        }
    }

    /** Muestra la red como texto: ubicaciones y conexiones con su tráfico. */
    static void red() {
        Red red = Datos.cargarRed(DATOS);
        System.out.println("Ubicaciones:");
        red.ubicaciones().forEach(u -> System.out.printf("  %-4s %s%n", u.id(), u.nombre()));
        System.out.println("Conexiones:");
        red.conexiones().forEach(c -> System.out.printf(Locale.US, "  %-4s <-> %-4s %6.1f km  tráfico %-5s peaje $%.2f%n",
                c.origen(), c.destino(), c.distanciaKm(), c.trafico(), c.peaje()));
    }

    static double medirMs(Runnable tarea) {
        long inicio = System.nanoTime();
        tarea.run();
        return (System.nanoTime() - inicio) / 1e6;
    }

    static void benchmark() {
        Red red = Datos.cargarRed(DATOS);
        // Calentamiento de la JVM (JIT) para no medir el arranque en frío.
        Concurrencia.calcularRutas(red, pedidosSinteticos(red, 500), false, 4);
        Concurrencia.calcularRutas(red, pedidosSinteticos(red, 500), true, 4);
        ListaEnlazada<String[]> filas = new ListaEnlazada<>();
        for (int n : new int[]{100, 1000, 5000}) {
            ListaEnlazada<Concurrencia.Pedido> pedidos = pedidosSinteticos(red, n);
            double seq = medirMs(() -> Concurrencia.calcularRutas(red, pedidos, false, 4));
            double conc = medirMs(() -> Concurrencia.calcularRutas(red, pedidos, true, 4));
            filas.agregarFinal(new String[]{"java", String.valueOf(n),
                    String.format(Locale.US, "%.1f", seq), String.format(Locale.US, "%.1f", conc)});
            System.out.printf(Locale.US, "n=%d: secuencial=%.1f ms, concurrente=%.1f ms%n", n, seq, conc);
        }
        Datos.escribirPares(SALIDA.resolve("benchmark_java.csv"), "lenguaje,n,secuencial_ms,concurrente_ms", filas);
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println(USO);
            System.exit(1);
        }
        try {
            switch (args[0]) {
                case "procesar" -> procesar();
                case "consultar" -> {
                    if (args.length < 3) {
                        throw new DatosInvalidosException(USO);
                    }
                    consultar(args[1], args[2]);
                }
                case "vehiculos" -> vehiculos();
                case "red" -> red();
                case "benchmark" -> benchmark();
                default -> {
                    System.out.println(USO);
                    System.exit(1);
                }
            }
        } catch (DatosInvalidosException e) {
            System.err.println("Error de datos: " + e.getMessage());
            System.exit(2);
        }
    }
}
