'use strict';
// Responsable: Integrante 2 (estructuras y concurrencia)

class Nodo {
  constructor(valor) {
    this.valor = valor;
    this.siguiente = null;
  }
}

/**
 * Cola de prioridad implementada como lista enlazada ordenada (estructura 2 de 2).
 * Atiende solicitudes (críticas primero) y sirve de frontera en la búsqueda de rutas.
 */
class ColaPrioridad {
  constructor(comparador) {
    this.comparador = comparador;
    this.frente = null;
    this.cantidad = 0;
  }

  /** Inserta en su posición; ante empate queda después de los existentes (FIFO). */
  encolar(valor) {
    const nuevo = new Nodo(valor);
    if (this.frente === null || this.comparador(this.frente.valor, valor) > 0) {
      nuevo.siguiente = this.frente;
      this.frente = nuevo;
    } else {
      let actual = this.frente;
      while (actual.siguiente !== null && this.comparador(actual.siguiente.valor, valor) <= 0) {
        actual = actual.siguiente;
      }
      nuevo.siguiente = actual.siguiente;
      actual.siguiente = nuevo;
    }
    this.cantidad++;
  }

  desencolar() {
    if (this.frente === null) throw new Error('La cola está vacía');
    const valor = this.frente.valor;
    this.frente = this.frente.siguiente;
    this.cantidad--;
    return valor;
  }

  estaVacia() {
    return this.frente === null;
  }

  tamano() {
    return this.cantidad;
  }
}

module.exports = { ColaPrioridad };
