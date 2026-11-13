package transporte;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Locale;

// Responsable: Integrante 4 (asignación, datos y CLI)

/** construcción de la red y escritura de resultados. */
public final class Datos {
    private Datos() { }

    /** Raíz del proyecto: funciona al ejecutar desde la raíz del repo o desde la carpeta java/. */
    public static Path raizProyecto() {
        Path actual = Path.of("").toAbsolutePath();
        return Files.isDirectory(actual.resolve("data")) ? actual : actual.getParent();
    }

    public static ListaEnlazada<Fila> leerCsv(Path ruta) {
        ListaEnlazada<Fila> filas = new ListaEnlazada<>();
        try (BufferedReader lector = Files.newBufferedReader(ruta)) {
            String encabezado = lector.readLine();
            if (encabezado == null) {
                throw new DatosInvalidosException("Archivo vacío: " + ruta);
            }
            String[] columnas = encabezado.split(",");
            String linea;
            while ((linea = lector.readLine()) != null) {
                if (!linea.isBlank()) {
                    filas.agregarFinal(new Fila(columnas, linea.split(",", -1)));
                }
            }
        } catch (NoSuchFileException e) {
            throw new DatosInvalidosException("No se encontró el archivo: " + ruta);
        } catch (IOException e) {
            throw new DatosInvalidosException("No se pudo leer " + ruta + ": " + e.getMessage());
        }
        return filas;
    }

    public static Red cargarRed(Path carpeta) {
        Red red = new Red();
        leerCsv(carpeta.resolve("ubicaciones.csv")).forEach(f -> red.registrarUbicacion(Ubicacion.desdeFila(f)));
        leerCsv(carpeta.resolve("conexiones.csv")).forEach(f -> red.registrarConexion(Conexion.desdeFila(f)));
        return red;
    }

    public static ListaEnlazada<Vehiculo> cargarVehiculos(Path carpeta) {
        return leerCsv(carpeta.resolve("vehiculos.csv")).transformar(Vehiculo::desdeFila);
    }

    public static ListaEnlazada<Solicitud> cargarSolicitudes(Path carpeta, Red red) {
        ListaEnlazada<Solicitud> solicitudes = leerCsv(carpeta.resolve("solicitudes.csv")).transformar(Solicitud::desdeFila);
        for (Solicitud s : solicitudes) {
            red.validarUbicacion(s.origen());
            red.validarUbicacion(s.destino());
        }
        return solicitudes;
    }

    public static String f2(double valor) {
        return String.format(Locale.US, "%.2f", valor);
    }

    public static void escribirPares(Path archivo, String encabezado, ListaEnlazada<String[]> filas) {
        try {
            Files.createDirectories(archivo.getParent());
            try (BufferedWriter escritor = Files.newBufferedWriter(archivo)) {
                escritor.write(encabezado + "\n");
                for (String[] fila : filas) {
                    escritor.write(String.join(",", fila) + "\n");
                }
            }
        } catch (IOException e) {
            throw new DatosInvalidosException("No se pudo escribir " + archivo + ": " + e.getMessage());
        }
    }

    public static void escribirResultados(Path archivo, ListaEnlazada<ResultadoSolicitud> resultados) {
        ListaEnlazada<String[]> filas = resultados.transformar(r -> {
            Ruta ruta = r.ruta();
            return new String[]{r.solicitud().id(), r.solicitud().prioridad(), r.solicitud().criterio(),
                    r.estado(), r.vehiculo(), ruta != null ? ruta.texto() : "-",
                    ruta != null ? f2(ruta.distanciaKm()) : "-", ruta != null ? f2(ruta.tiempoMin()) : "-",
                    ruta != null ? f2(ruta.costo()) : "-", r.cumpleSla()};
        });
        escribirPares(archivo, "solicitud,prioridad,criterio,estado,vehiculo,ruta,distancia_km,tiempo_min,costo,cumple_sla", filas);
    }
}
