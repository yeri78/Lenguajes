package transporte;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

// Responsable: Integrante 2 (estructuras y concurrencia)

/** Calcular rutas */
public final class Concurrencia {
    private Concurrencia() { }

    /** Pedido de ruta: origen, destino y criterio. */
    public record Pedido(String origen, String destino, String criterio) { }

    /** Trabajo por solicitud: enumera rutas posibles y elige la mejor. */
    static Ruta calcularUna(Red red, Pedido p) {
        Rutas.todasLasRutas(red, p.origen(), p.destino());
        return Rutas.mejorRuta(red, p.origen(), p.destino(), p.criterio());
    }

    /** Devuelve las rutas en el mismo orden de los pedidos (null si no hay camino). */
    public static ListaEnlazada<Ruta> calcularRutas(Red red, ListaEnlazada<Pedido> pedidos, boolean concurrente, int hilos) {
        if (!concurrente) {
            return pedidos.transformar(p -> calcularUna(red, p));
        }
        ExecutorService pool = Executors.newFixedThreadPool(hilos);
        try {
            ListaEnlazada<Future<Ruta>> futuros = new ListaEnlazada<>();
            for (Pedido p : pedidos) {
                futuros.agregarFinal(pool.submit(() -> calcularUna(red, p)));
            }
            ListaEnlazada<Ruta> resultado = new ListaEnlazada<>();
            for (Future<Ruta> futuro : futuros) {
                resultado.agregarFinal(futuro.get());
            }
            return resultado;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Cálculo concurrente interrumpido", e);
        } catch (ExecutionException e) {
            throw new IllegalStateException("Fallo en el cálculo concurrente", e);
        } finally {
            pool.shutdown();
        }
    }
}