'use strict';
// Responsable: Integrante 3 (red, rutas y estadísticas)

/** Camino (lista enlazada de ids de ubicación) con sus totales. */
class Ruta {
  constructor(nodos, distanciaKm, tiempoMin, costo) {
    Object.assign(this, { nodos, distanciaKm, tiempoMin, costo });
  }

  texto() {
    return this.nodos.unir('->');
  }
}

module.exports = { Ruta };