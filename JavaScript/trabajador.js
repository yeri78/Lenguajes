'use strict';
// Responsable: Integrante 2 (estructuras y concurrencia)
// Hilo trabajador: reconstruye la red y calcula un bloque de pedidos.
const { parentPort, workerData } = require('node:worker_threads');
const { Red } = require('./red');
const { Ubicacion, Conexion } = require('./modelos');
const { calcularUna } = require('./calculo');

const red = new Red();
for (const u of workerData.ubicaciones) red.registrarUbicacion(new Ubicacion(u.id, u.nombre, u.x, u.y));
for (const c of workerData.conexiones) {
  red.registrarConexion(new Conexion(c.origen, c.destino, c.distanciaKm, c.trafico, c.peaje));
}

const resultado = [];
for (const [origen, destino, criterio] of workerData.pedidos) {
  const ruta = calcularUna(red, { origen, destino, criterio });
  resultado.push(ruta
    ? { nodos: ruta.nodos.aArreglo(), distanciaKm: ruta.distanciaKm, tiempoMin: ruta.tiempoMin, costo: ruta.costo }
    : null);
}
parentPort.postMessage(resultado);