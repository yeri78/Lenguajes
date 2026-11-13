package transporte;

import java.util.function.Predicate;

// Responsable: Integrante 1 (modelos y validación)

/** Funciones de validación compartidas por los modelos. */
public final class Validacion {
    private Validacion() { }

    public static String requerirTexto(Fila fila, String campo) {
        String valor = fila.obtener(campo);
        if (valor == null || valor.isBlank()) {
            throw new DatosInvalidosException("El campo '" + campo + "' no puede estar vacío");
        }
        return valor.trim();
    }

    /** estrictamentePositivo=true exige > 0; false exige >= 0. */
    public static double requerirNumero(Fila fila, String campo, boolean estrictamentePositivo) {
        String texto = requerirTexto(fila, campo);
        double numero;
        try {
            numero = Double.parseDouble(texto);
        } catch (NumberFormatException e) {
            throw new DatosInvalidosException("El campo '" + campo + "' debe ser numérico: " + texto);
        }
        if (estrictamentePositivo && numero <= 0) {
            throw new DatosInvalidosException("El campo '" + campo + "' debe ser mayor que cero: " + texto);
        }
        if (!estrictamentePositivo && numero < 0) {
            throw new DatosInvalidosException("El campo '" + campo + "' no puede ser negativo: " + texto);
        }
        return numero;
    }

    public static int requerirEntero(Fila fila, String campo) {
        double numero = requerirNumero(fila, campo, true);
        if (numero != Math.rint(numero)) {
            throw new DatosInvalidosException("El campo '" + campo + "' debe ser entero: " + numero);
        }
        return (int) numero;
    }

    /** Recibe una función (Predicate) que decide si el valor es válido. */
    public static String requerirOpcion(Fila fila, String campo, Predicate<String> esValida, String opciones) {
        String texto = requerirTexto(fila, campo).toUpperCase();
        if (!esValida.test(texto)) {
            throw new DatosInvalidosException("'" + campo + "' inválido: " + texto + ". Opciones: " + opciones);
        }
        return texto;
    }
}