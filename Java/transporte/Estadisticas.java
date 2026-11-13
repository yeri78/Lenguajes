package transporte;

// Responsable: Integrante 3 (red, rutas y estadísticas)

/** resumen del procesamiento. */
public final class Estadisticas {
    private Estadisticas() { }

    private static void agregar(ListaEnlazada<String[]> lista, String metrica, String valor) {
        lista.agregarFinal(new String[]{metrica, valor});
    }

    public static ListaEnlazada<String[]> resumir(ListaEnlazada<ResultadoSolicitud> resultados,
                                                  Asignacion.GestorFlota flota) {
        ListaEnlazada<ResultadoSolicitud> asignadas = resultados.filtrar(r -> r.estado().equals("ASIGNADA"));
        ListaEnlazada<ResultadoSolicitud> conRuta = resultados.filtrar(r -> r.ruta() != null);
        int cumplen = asignadas.contar(r -> r.cumpleSla().equals("SI"));
        double promedio = conRuta.estaVacia() ? 0 : conRuta.sumar(r -> r.ruta().tiempoMin()) / conRuta.tamano();
        double porcentaje = asignadas.estaVacia() ? 0 : 100.0 * cumplen / asignadas.tamano();

        ListaEnlazada<String[]> resumen = new ListaEnlazada<>();
        agregar(resumen, "total_solicitudes", String.valueOf(resultados.tamano()));
        agregar(resumen, "asignadas", String.valueOf(asignadas.tamano()));
        agregar(resumen, "en_cola", String.valueOf(resultados.contar(r -> r.estado().equals("EN_COLA"))));
        agregar(resumen, "sin_ruta", String.valueOf(resultados.contar(r -> r.estado().equals("SIN_RUTA"))));
        agregar(resumen, "vehiculos_disponibles", String.valueOf(flota.disponibles().tamano()));
        agregar(resumen, "vehiculos_ocupados", String.valueOf(flota.ocupados().tamano()));
        agregar(resumen, "distancia_total_km", Datos.f2(asignadas.sumar(r -> r.ruta().distanciaKm())));
        agregar(resumen, "costo_total", Datos.f2(asignadas.sumar(r -> r.ruta().costo())));
        agregar(resumen, "tiempo_promedio_min", Datos.f2(promedio));
        agregar(resumen, "cumplen_sla", String.valueOf(cumplen));
        agregar(resumen, "porcentaje_sla", Datos.f2(porcentaje));
        return resumen;
    }
}