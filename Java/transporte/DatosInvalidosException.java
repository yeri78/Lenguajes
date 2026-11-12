package transporte;

// Responsable: Integrante 1 (modelos y validación)

/** se lanza cuando un dato de entrada no esta cumpliendo las reglas del negocio */
public class DatosInvalidosException extends RuntimeException {
    public DatosInvalidosException(String mensaje) {
        super(mensaje);
    }
}