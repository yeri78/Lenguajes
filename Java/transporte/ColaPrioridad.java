package transporte;

import java.util.Comparator;
import java.util.NoSuchElementException;

// Responsable: Integrante 2 (estructuras y concurrencia)

/**
 la prioridad es una lista enlazada ordenada (estructura 2 de 2).  la usamos para atender solicitudes
 */
public class ColaPrioridad<T> {

    private static final class Nodo<T> {
        private final T valor;
        private Nodo<T> siguiente;

        private Nodo(T valor) {
            this.valor = valor;
        }
    }

    private final Comparator<T> comparador;
    private Nodo<T> frente;
    private int tamano;

    public ColaPrioridad(Comparator<T> comparador) {
        this.comparador = comparador;
    }

    /** Inserta en su posición; ante empate queda después de los existentes (FIFO). */
    public void encolar(T valor) {
        Nodo<T> nuevo = new Nodo<>(valor);
        if (frente == null || comparador.compare(frente.valor, valor) > 0) {
            nuevo.siguiente = frente;
            frente = nuevo;
        } else {
            Nodo<T> actual = frente;
            while (actual.siguiente != null && comparador.compare(actual.siguiente.valor, valor) <= 0) {
                actual = actual.siguiente;
            }
            nuevo.siguiente = actual.siguiente;
            actual.siguiente = nuevo;
        }
        tamano++;
    }

    public T desencolar() {
        if (frente == null) {
            throw new NoSuchElementException("La cola está vacía");
        }
        T valor = frente.valor;
        frente = frente.siguiente;
        tamano--;
        return valor;
    }

    public boolean estaVacia() {
        return frente == null;
    }

    public int tamano() {
        return tamano;
    }
}