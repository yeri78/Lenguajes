package transporte;

// Responsable: Integrante 1 (modelos y validación)

public record Solicitud(String id, String origen, String destino, String prioridad, String criterio, int pasajeros) {
    public static Solicitud desdeFila(Fila fila) {
        String origen = Validacion.requerirTexto(fila, "origen");
        String destino = Validacion.requerirTexto(fila, "destino");
        if (origen.equals(destino)) {
            throw new DatosInvalidosException("Origen y destino de la solicitud deben ser distintos");
        }
        return new Solicitud(Validacion.requerirTexto(fila, "id"), origen, destino,
                Validacion.requerirOpcion(fila, "prioridad", Constantes::esPrioridad, "CRITICA, ALTA, MEDIA, BAJA"),
                Validacion.requerirOpcion(fila, "criterio", Constantes::esCriterio, "DISTANCIA, TIEMPO, COSTO"),
                Validacion.requerirEntero(fila, "pasajeros"));
    }
}