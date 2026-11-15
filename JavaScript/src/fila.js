'use strict';
// Responsable: Integrante 1 (modelos y validación)
const { ListaEnlazada } = require('./listaEnlazada');

/** Una fila de CSV: columnas y celdas guardadas en listas enlazadas. */
class Fila {
  constructor(columnas, celdas) {
    this.columnas = columnas;
    this.celdas = celdas;
  }

  /** Crea una fila desde pares clave, valor, clave, valor... (útil en pruebas). */
  static de(...pares) {
    const columnas = new ListaEnlazada();
    const celdas = new ListaEnlazada();
    for (let i = 0; i + 1 < pares.length; i += 2) {
      columnas.agregarFinal(pares[i]);
      celdas.agregarFinal(pares[i + 1]);
    }
    return new Fila(columnas, celdas);
  }

  static desdeTexto(encabezado, linea) {
    return new Fila(ListaEnlazada.desdeArreglo(encabezado.split(',')), ListaEnlazada.desdeArreglo(linea.split(',')));
  }

  /** Valor de la columna, o null si la columna no existe. */
  obtener(campo) {
    const siguienteCelda = this.celdas[Symbol.iterator]();
    for (const columna of this.columnas) {
      const celda = siguienteCelda.next();
      if (columna.trim() === campo) return celda.done ? '' : String(celda.value).trim();
    }
    return null;
  }

  obtenerOpcional(campo, defecto) {
    const valor = this.obtener(campo);
    return (valor === null || valor === '') ? defecto : valor;
  }
}

module.exports = { Fila };