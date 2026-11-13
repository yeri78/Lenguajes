package transporte;

// Responsable: Integrante 4 (asignación, datos y CLI)

/** estado: ASIGNADA | EN_COLA | SIN_RUTA. ruta puede ser null. */
public record ResultadoSolicitud(Solicitud solicitud, String estado, Ruta ruta, String vehiculo, String cumpleSla) {
}
