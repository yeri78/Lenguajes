'use strict';
// Responsable: Integrante 3 (red, rutas y estadísticas)
// Búsqueda de rutas: todas las rutas simples (recursión) y la mejor (Dijkstra con ColaPrioridad).
const { ListaEnlazada } = require('./listaEnlazada');
const { ColaPrioridad } = require('./colaPrioridad');
const { Ruta } = require('./ruta');

function compararNodos(a, b) {
  const siguienteB = b[Symbol.iterator]();
  for (const x of a) {
    const y = siguienteB.next();
    if (y.done) return 1;
    if (x < y.value) return -1;
    if (x > y.value) return 1;
  }
  return siguienteB.next().done ? 0 : -1;
}

/** Suma distancia, tiempo y costo recorriendo los tramos en orden. */
function construirRuta(red, nodos) {
  let distancia = 0.0;
  let tiempo = 0.0;
  let costo = 0.0;
  let anterior = null;
  for (const nodo of nodos) {
    if (anterior !== null) {
      const tramo = red.buscarConexion(anterior, nodo);
      distancia += tramo.distanciaKm;
      tiempo += tramo.tiempoMin();
      costo += tramo.costo();
    }
    anterior = nodo;
  }
  return new Ruta(nodos.copiar(), distancia, tiempo, costo);
}

function explorar(red, actual, destino, camino, salida) {
  if (actual === destino) {
    salida.agregarFinal(construirRuta(red, camino));
    return;
  }
  for (const tramo of red.vecinos(actual)) {
    if (!camino.contieneValor(tramo.destino)) {
      camino.agregarFinal(tramo.destino);
      explorar(red, tramo.destino, destino, camino, salida);
      camino.eliminarUltimo();
    }
  }
}

/** Todas las rutas simples (sin repetir ubicaciones), ordenadas por su camino. */
function todasLasRutas(red, origen, destino) {
  red.validarUbicacion(origen);
  red.validarUbicacion(destino);
  const encontradas = new ListaEnlazada();
  const camino = new ListaEnlazada();
  camino.agregarFinal(origen);
  explorar(red, origen, destino, camino, encontradas);
  return encontradas.ordenada((a, b) => compararNodos(a.nodos, b.nodos));
}

/** Dijkstra. Desempata por orden lexicográfico del camino (determinista). Devuelve null si no hay ruta. */
function mejorRuta(red, origen, destino, criterio) {
  red.validarUbicacion(origen);
  red.validarUbicacion(destino);
  const frontera = new ColaPrioridad((a, b) => {
    if (a.peso < b.peso) return -1;
    if (a.peso > b.peso) return 1;
    return compararNodos(a.camino, b.camino);
  });
  const inicio = new ListaEnlazada();
  inicio.agregarFinal(origen);
  frontera.encolar({ peso: 0.0, camino: inicio });
  const visitados = new ListaEnlazada();
  while (!frontera.estaVacia()) {
    const actual = frontera.desencolar();
    const nodo = actual.camino.ultimo();
    if (visitados.contieneValor(nodo)) continue;
    visitados.agregarFinal(nodo);
    if (nodo === destino) return construirRuta(red, actual.camino);
    for (const tramo of red.vecinos(nodo)) {
      if (!visitados.contieneValor(tramo.destino)) {
        const camino = actual.camino.copiar();
        camino.agregarFinal(tramo.destino);
        frontera.encolar({ peso: actual.peso + tramo.peso(criterio), camino });
      }
    }
  }
  return null;
}

module.exports = { compararNodos, construirRuta, todasLasRutas, mejorRuta };