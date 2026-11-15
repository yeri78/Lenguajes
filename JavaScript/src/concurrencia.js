'use strict';
// Responsable: Integrante 2 (estructuras y concurrencia)
// Cálculo de rutas para muchas solicitudes, secuencial o en paralelo (worker_threads).
const path = require('node:path');
const { Worker } = require('node:worker_threads');
const { ListaEnlazada } = require('./listaEnlazada');
const { Ruta } = require('./ruta');
const { calcularUna } = require('./calculo');

/** pedidos: lista de { origen, destino, criterio }. Devuelve rutas en el mismo orden (null si no hay camino). */
function calcularRutasSecuencial(red, pedidos) {
  return pedidos.transformar((pedido) => calcularUna(red, pedido));
}

function lanzarHilo(datosRed, bloque) {
  return new Promise((resolver, rechazar) => {
    const hilo = new Worker(path.join(__dirname, 'trabajador.js'),
      { workerData: { ...datosRed, pedidos: bloque } });
    hilo.once('message', resolver);
    hilo.once('error', rechazar);
  });
}

/** Reparte los pedidos en bloques contiguos, uno por hilo, y conserva el orden de entrada. */
async function calcularRutasConcurrente(red, pedidos, hilos = 4) {
  const resultado = new ListaEnlazada();
  if (pedidos.estaVacia()) return resultado;

  const datosRed = {
    ubicaciones: red.ubicaciones().transformar((u) => ({ id: u.id, nombre: u.nombre, x: u.x, y: u.y })).aArreglo(),
    conexiones: red.conexiones().transformar((c) => ({
      origen: c.origen, destino: c.destino, distanciaKm: c.distanciaKm, trafico: c.trafico, peaje: c.peaje,
    })).aArreglo(),
  };
  const tamanoBloque = Math.max(1, Math.ceil(pedidos.tamano() / hilos));
  const bloques = [];
  let bloque = [];
  for (const p of pedidos) {
    bloque.push([p.origen, p.destino, p.criterio]);
    if (bloque.length === tamanoBloque) {
      bloques.push(bloque);
      bloque = [];
    }
  }
  if (bloque.length > 0) bloques.push(bloque);

  const partes = await Promise.all(bloques.map((b) => lanzarHilo(datosRed, b)));
  for (const parte of partes) {
    for (const r of parte) {
      resultado.agregarFinal(r
        ? new Ruta(ListaEnlazada.desdeArreglo(r.nodos), r.distanciaKm, r.tiempoMin, r.costo)
        : null);
    }
  }
  return resultado;
}

module.exports = { calcularRutasSecuencial, calcularRutasConcurrente };