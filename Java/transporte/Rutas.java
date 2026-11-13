package transporte;

import java.util.Comparator;
import java.util.Iterator;

// Responsable: Integrante 3 (red, rutas y estadísticas)

/** busca las rutas simples (recursión) y la mejor (Dijkstra con ColaPrioridad). */
public final class Rutas {
    private Rutas() { }

    static int compararNodos(ListaEnlazada<String> a, ListaEnlazada<String> b) {
        Iterator<String> ia = a.iterator();
        Iterator<String> ib = b.iterator();
        while (ia.hasNext() && ib.hasNext()) {
            int c = ia.next().compareTo(ib.next());
            if (c != 0) {
                return c;
            }
        }
        return Integer.compare(a.tamano(), b.tamano());
    }

    /** suma distancia, tiempo y costo recorriendo tramos en orden. */
    public static Ruta construirRuta(Red red, ListaEnlazada<String> nodos) {
        double distancia = 0.0, tiempo = 0.0, costo = 0.0;
        String anterior = null;
        for (String nodo : nodos) {
            if (anterior != null) {
                Conexion tramo = red.buscarConexion(anterior, nodo);
                distancia += tramo.distanciaKm();
                tiempo += tramo.tiempoMin();
                costo += tramo.costo();
            }
            anterior = nodo;
        }
        return new Ruta(nodos.copiar(), distancia, tiempo, costo);
    }

    /**  rutas simples (sin repetir ubicaciones), ordenadas por camino. */
    public static ListaEnlazada<Ruta> todasLasRutas(Red red, String origen, String destino) {
        red.validarUbicacion(origen);
        red.validarUbicacion(destino);
        ListaEnlazada<Ruta> encontradas = new ListaEnlazada<>();
        ListaEnlazada<String> camino = new ListaEnlazada<>();
        camino.agregarFinal(origen);
        explorar(red, origen, destino, camino, encontradas);
        return encontradas.ordenada((a, b) -> compararNodos(a.nodos(), b.nodos()));
    }

    private static void explorar(Red red, String actual, String destino, ListaEnlazada<String> camino,
                                 ListaEnlazada<Ruta> salida) {
        if (actual.equals(destino)) {
            salida.agregarFinal(construirRuta(red, camino));
            return;
        }
        for (Conexion tramo : red.vecinos(actual)) {
            if (!camino.contieneValor(tramo.destino())) {
                camino.agregarFinal(tramo.destino());
                explorar(red, tramo.destino(), destino, camino, salida);
                camino.eliminarUltimo();
            }
        }
    }

    private record Entrada(double peso, ListaEnlazada<String> camino) { }

    /** desempata por orden lexicográfico del camino. null si no hay ruta. */
    public static Ruta mejorRuta(Red red, String origen, String destino, String criterio) {
        red.validarUbicacion(origen);
        red.validarUbicacion(destino);
        ColaPrioridad<Entrada> frontera = new ColaPrioridad<>(
                Comparator.<Entrada>comparingDouble(Entrada::peso)
                        .thenComparing((a, b) -> compararNodos(a.camino(), b.camino())));
        ListaEnlazada<String> inicio = new ListaEnlazada<>();
        inicio.agregarFinal(origen);
        frontera.encolar(new Entrada(0.0, inicio));
        ListaEnlazada<String> visitados = new ListaEnlazada<>();
        while (!frontera.estaVacia()) {
            Entrada actual = frontera.desencolar();
            String nodo = actual.camino().ultimo();
            if (visitados.contieneValor(nodo)) {
                continue;
            }
            visitados.agregarFinal(nodo);
            if (nodo.equals(destino)) {
                return construirRuta(red, actual.camino());
            }
            for (Conexion tramo : red.vecinos(nodo)) {
                if (!visitados.contieneValor(tramo.destino())) {
                    ListaEnlazada<String> camino = actual.camino().copiar();
                    camino.agregarFinal(tramo.destino());
                    frontera.encolar(new Entrada(actual.peso() + tramo.peso(criterio), camino));
                }
            }
        }
        return null;
    }
}