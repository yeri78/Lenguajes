'use strict';
// Responsable: Integrante 2 (estructuras y concurrencia)

class Nodo {
  constructor(valor) {
    this.valor = valor;
    this.siguiente = null;
  }
}

/**
 * Lista enlazada simple (estructura 1 de 2).
 * Guarda ubicaciones, conexiones, vehículos, solicitudes, resultados y los caminos de las rutas.
 * filtrar/transformar/contar/sumar/minimo reciben funciones (orden superior).
 * Los arreglos de JavaScript solo se usan en los bordes: leer texto y pasar datos a worker_threads.
 */
class ListaEnlazada {
  constructor() {
    this.cabeza = null;
    this.cola = null;
    this.cantidad = 0;
  }

  static desdeArreglo(arreglo) {
    const lista = new ListaEnlazada();
    for (const valor of arreglo) lista.agregarFinal(valor);
    return lista;
  }

  agregarFinal(valor) {
    const nuevo = new Nodo(valor);
    if (this.cabeza === null) this.cabeza = nuevo;
    else this.cola.siguiente = nuevo;
    this.cola = nuevo;
    this.cantidad++;
  }

  agregarInicio(valor) {
    const nuevo = new Nodo(valor);
    nuevo.siguiente = this.cabeza;
    this.cabeza = nuevo;
    if (this.cola === null) this.cola = nuevo;
    this.cantidad++;
  }

  eliminarUltimo() {
    if (this.cabeza === null) throw new Error('La lista está vacía');
    const valor = this.cola.valor;
    if (this.cabeza === this.cola) {
      this.cabeza = null;
      this.cola = null;
    } else {
      let anterior = this.cabeza;
      while (anterior.siguiente !== this.cola) anterior = anterior.siguiente;
      anterior.siguiente = null;
      this.cola = anterior;
    }
    this.cantidad--;
    return valor;
  }

  ultimo() {
    if (this.cola === null) throw new Error('La lista está vacía');
    return this.cola.valor;
  }

  obtener(indice) {
    if (!Number.isInteger(indice) || indice < 0 || indice >= this.cantidad) {
      throw new RangeError(`Índice fuera de rango: ${indice}`);
    }
    let actual = this.cabeza;
    for (let i = 0; i < indice; i++) actual = actual.siguiente;
    return actual.valor;
  }

  tamano() {
    return this.cantidad;
  }

  estaVacia() {
    return this.cantidad === 0;
  }

  *[Symbol.iterator]() {
    let actual = this.cabeza;
    while (actual !== null) {
      yield actual.valor;
      actual = actual.siguiente;
    }
  }

  forEach(funcion) {
    for (const valor of this) funcion(valor);
  }

  /** Devuelve el primer elemento que cumple la condición, o null. */
  buscar(condicion) {
    for (const valor of this) if (condicion(valor)) return valor;
    return null;
  }

  contiene(condicion) {
    for (const valor of this) if (condicion(valor)) return true;
    return false;
  }

  contieneValor(valor) {
    return this.contiene((x) => x === valor);
  }

  filtrar(condicion) {
    const resultado = new ListaEnlazada();
    for (const valor of this) if (condicion(valor)) resultado.agregarFinal(valor);
    return resultado;
  }

  transformar(funcion) {
    const resultado = new ListaEnlazada();
    for (const valor of this) resultado.agregarFinal(funcion(valor));
    return resultado;
  }

  contar(condicion) {
    return this.filtrar(condicion).tamano();
  }

  sumar(funcion) {
    let total = 0.0;
    for (const valor of this) total += funcion(valor);
    return total;
  }

  /** Elemento menor según el comparador, o null si la lista está vacía. */
  minimo(comparador) {
    let mejor = null;
    let hay = false;
    for (const valor of this) {
      if (!hay || comparador(valor, mejor) < 0) {
        mejor = valor;
        hay = true;
      }
    }
    return mejor;
  }

  copiar() {
    const copia = new ListaEnlazada();
    for (const valor of this) copia.agregarFinal(valor);
    return copia;
  }

  /** Inserta manteniendo el orden; los iguales quedan después (estable). */
  insertarOrdenado(valor, comparador) {
    if (this.cabeza === null || comparador(this.cabeza.valor, valor) > 0) {
      this.agregarInicio(valor);
      return;
    }
    let actual = this.cabeza;
    while (actual.siguiente !== null && comparador(actual.siguiente.valor, valor) <= 0) {
      actual = actual.siguiente;
    }
    const nuevo = new Nodo(valor);
    nuevo.siguiente = actual.siguiente;
    actual.siguiente = nuevo;
    if (actual === this.cola) this.cola = nuevo;
    this.cantidad++;
  }

  ordenada(comparador) {
    const resultado = new ListaEnlazada();
    for (const valor of this) resultado.insertarOrdenado(valor, comparador);
    return resultado;
  }

  unir(separador) {
    let texto = '';
    let primero = true;
    for (const valor of this) {
      if (!primero) texto += separador;
      texto += String(valor);
      primero = false;
    }
    return texto;
  }

  equals(otra, iguales = (a, b) => a === b) {
    if (!(otra instanceof ListaEnlazada) || otra.cantidad !== this.cantidad) return false;
    const siguiente = otra[Symbol.iterator]();
    for (const valor of this) {
      if (!iguales(valor, siguiente.next().value)) return false;
    }
    return true;
  }

  /** Solo para pasar datos a hilos (worker_threads). */
  aArreglo() {
    const arreglo = [];
    for (const valor of this) arreglo.push(valor);
    return arreglo;
  }

  toString() {
    return `[${this.unir(', ')}]`;
  }
}

module.exports = { ListaEnlazada };