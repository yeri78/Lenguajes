package transporte;

// Responsable: Integrante 1 (modelos y validación)

public record Ubicacion(String id, String nombre, double x, double y) {
    public static Ubicacion desdeFila(Fila fila) {
        return new Ubicacion(Validacion.requerirTexto(fila, "id"), Validacion.requerirTexto(fila, "nombre"),
                Double.parseDouble(fila.obtenerOpcional("x", "0")), Double.parseDouble(fila.obtenerOpcional("y", "0")));
    }
}