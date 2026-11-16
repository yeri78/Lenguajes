'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI). uso principal: procesar todas las solicitudes del conjunto de datos.
const { ListaEnlazada } = require('./listaEnlazada');
const { GestorFlota, asignarSolicitudes } = require('./asignacion');
const { calcularRutasSecuencial, calcularRutasConcurrente } = require('./concurrencia');
const { resumir } = require('./estadisticas');

async function procesar(red, vehiculos, solicitudes, concurrente = true) {
  // 1) Parte paralelizable: calcular la ruta de cada solicitud.
  const pedidos = solicitudes.transformar((s) => ({ origen: s.origen, destino: s.destino, criterio: s.criterio }));
  const rutas = concurrente
    ? await calcularRutasConcurrente(red, pedidos)
    : calcularRutasSecuencial(red, pedidos);

  // 2) Parte secuencial: asignar vehículos respetando la prioridad.
  const pendientes = new ListaEnlazada();
  const siguienteRuta = rutas[Symbol.iterator]();
  for (const solicitud of solicitudes) {
    pendientes.agregarFinal({ solicitud, ruta: siguienteRuta.next().value });
  }
  const flota = new GestorFlota(vehiculos);
  const resultados = asignarSolicitudes(pendientes, flota);
  return { resultados, resumen: resumir(resultados, flota), flota };
}

module.exports = { procesar };
