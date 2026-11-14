'use strict';
// Responsable: Integrante 2 (estructuras y concurrencia)
const { todasLasRutas, mejorRuta } = require('./rutas');

/** Trabajo por solicitud: enumera rutas posibles y elige la mejor. */
function calcularUna(red, pedido) {
  todasLasRutas(red, pedido.origen, pedido.destino);
  return mejorRuta(red, pedido.origen, pedido.destino, pedido.criterio);
}

module.exports = { calcularUna };