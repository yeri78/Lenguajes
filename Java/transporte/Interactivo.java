package transporte;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Optional;
import java.util.Scanner;

// Responsable: Integrante 4 (asignación, datos y CLI)

/** ver rutas, elegir una, asignar vehículo y conductor. */
public class Interactivo {
    private final Red red;
    private final ListaEnlazada<Vehiculo> vehiculos;
    private final Asignacion.GestorFlota flota;
    private final Scanner teclado = new Scanner(System.in);
    private int contador = 0;

    public Interactivo(Red red, ListaEnlazada<Vehiculo> vehiculos) {
        this.red = red;
        this.vehiculos = vehiculos;
        this.flota = new Asignacion.GestorFlota(vehiculos);
    }

    public static void main(String[] args) {
        try {
            Path datos = Datos.raizProyecto().resolve("data");
            new Interactivo(Datos.cargarRed(datos), Datos.cargarVehiculos(datos)).ejecutar();
        } catch (DatosInvalidosException e) {
            System.err.println("Error de datos: " + e.getMessage());
        }
    }

    public void ejecutar() {
        String opcion = "";
        while (!opcion.equals("0")) {
            System.out.println("\n1) Ver red   2) Consultar rutas y asignar viaje   3) Ver vehículos");
            System.out.println("4) Finalizar viaje   5) Cambiar trafico de un tramo   0) Salir");
            opcion = leer("Elige una opcion: ");
            try {
                switch (opcion) {
                    case "1" -> verRed();
                    case "2" -> consultarYAsignar();
                    case "3" -> verVehiculos();
                    case "4" -> finalizarViaje();
                    case "5" -> cambiarTrafico();
                    case "0" -> System.out.println("Hasta luego.");
                    default -> System.out.println("Opción no válida.");
                }
            } catch (DatosInvalidosException e) {
                System.out.println("Dato inválido: " + e.getMessage());
            } catch (NumberFormatException e) {
                System.out.println("Debes escribir un numero válido.");
            }
        }
    }
    /**  Lee una línea; si ya no hay entrada devuelve "0" para salir. */
    private String leer(String mensaje) {
        System.out.print(mensaje);
        return teclado.hasNextLine() ? teclado.nextLine().trim() : "0";
    }

    private static String tiempo(double minutos) {
        int total = (int) Math.round(minutos);
        return total >= 60 ? (total / 60) + " h " + (total % 60) + " min" : total + " min";
    }

    private void verRed() {
        System.out.println("Ubicaciones:");
        red.ubicaciones().forEach(u -> System.out.println("  " + u.id() + " " + u.nombre()));
        System.out.println("Conexiones:");
        red.conexiones().forEach(c -> System.out.println("  " + c.origen() + " <-> " + c.destino() + "  "
                + c.distanciaKm() + " km  trafico " + c.trafico() + "  peaje $" + c.peaje()));
    }

    private void verVehiculos() {
        System.out.println("Disponibles:");
        flota.disponibles().forEach(v -> System.out.println("  " + v.id() + " " + v.tipo()
                + " (cap. " + v.capacidad() + ") conductor: " + v.conductor()));
        System.out.println("Ocupados:");
        flota.ocupados().forEach(v -> System.out.println("  " + v.id() + " " + v.tipo()
                + " (cap. " + v.capacidad() + ") conductor: " + v.conductor()));
    }

    private void consultarYAsignar() {
        String origen = leer("Origen (ej. L1): ").toUpperCase();
        String destino = leer("Destino (ej. L7): ").toUpperCase();
        if (origen.equals(destino)) {
            throw new DatosInvalidosException("Origen y destino deben ser distintos");
        }
        ListaEnlazada<Ruta> rutas = Rutas.todasLasRutas(red, origen, destino)
                .ordenada(Comparator.comparingDouble(Ruta::tiempoMin));
        if (rutas.estaVacia()) {
            System.out.println("No hay ruta entre " + origen + " y " + destino);
            return;
        }
        String corta = Rutas.mejorRuta(red, origen, destino, "DISTANCIA").texto();
        String rapida = Rutas.mejorRuta(red, origen, destino, "TIEMPO").texto();
        String barata = Rutas.mejorRuta(red, origen, destino, "COSTO").texto();

        System.out.println("Rutas disponibles (de menor a mayor tiempo, con trafico incluido):");
        int numero = 1;
        for (Ruta r : rutas) {
            String marcas = (r.texto().equals(corta) ? " [MAS CORTA]" : "")
                    + (r.texto().equals(rapida) ? " [MENOR TIEMPO]" : "")
                    + (r.texto().equals(barata) ? " [MENOR COSTO]" : "");
            System.out.println("  " + numero++ + ") " + r.texto() + " | " + Datos.f2(r.distanciaKm()) + " km | "
                    + tiempo(r.tiempoMin()) + " | $" + Datos.f2(r.costo()) + marcas);
        }

        int eleccion = Integer.parseInt(leer("Número de ruta (0 = cancelar): "));
        if (eleccion == 0) {
            return;
        }
        if (eleccion < 1 || eleccion > rutas.tamano()) {
            throw new DatosInvalidosException("Número de ruta fuera de rango");
        }
        Ruta ruta = rutas.obtener(eleccion - 1);
        Solicitud solicitud = Solicitud.desdeFila(Fila.de("id", "M" + (++contador), "origen", origen,
                "destino", destino, "criterio", "TIEMPO",
                "pasajeros", leer("Pasajeros: "),
                "prioridad", leer("Prioridad (CRITICA/ALTA/MEDIA/BAJA): ").toUpperCase()));

        Optional<Vehiculo> vehiculo = flota.asignar(solicitud.pasajeros());
        if (vehiculo.isEmpty()) {
            System.out.println("No hay vehículo disponible para " + solicitud.pasajeros() + " pasajeros.");
            return;
        }
        System.out.println("\nSolicitud " + solicitud.id() + " ASIGNADA");
        System.out.println("  Vehículo:  " + vehiculo.get().id() + " (" + vehiculo.get().tipo() + ")");
        System.out.println("  Conductor: " + vehiculo.get().conductor());
        System.out.println("  Ruta:      " + ruta.texto());
        System.out.println("  Tiempo estimado: " + tiempo(ruta.tiempoMin()) + " | Costo: $" + Datos.f2(ruta.costo()));
        System.out.println("  Tiempo máximo de respuesta (" + solicitud.prioridad() + "): "
                + Constantes.horasMaxRespuesta(solicitud.prioridad()) + " h -> "
                + (Asignacion.cumpleSla(solicitud, ruta) ? "SI cumple" : "NO cumple"));
    }

    private void finalizarViaje() {
        String id = leer("Id del vehículo que terminó (ej. V1): ").toUpperCase();
        Vehiculo vehiculo = vehiculos.buscar(v -> v.id().equals(id))
                .orElseThrow(() -> new DatosInvalidosException("Vehículo no registrado: " + id));
        vehiculo.liberar();
        System.out.println("Vehículo " + id + " disponible de nuevo.");
    }

    private void cambiarTrafico() {
        String a = leer("Ubicación A: ").toUpperCase();
        String b = leer("Ubicación B: ").toUpperCase();
        String trafico = leer("Nuevo tráfico (BAJO/MEDIO/ALTO): ").toUpperCase();
        red.cambiarTrafico(a, b, trafico);
        System.out.println("Listo. Consulta rutas de nuevo para ver el efecto.");
    }
}