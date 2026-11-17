'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI)
// CLI: node src/main.js procesar | consultar ORIGEN DESTINO | vehiculos | red | benchmark | interactivo
const path = require('node:path');
const { ListaEnlazada } = require('./listaEnlazada');
const { raizProyecto, cargarRed, cargarVehiculos, cargarSolicitudes, escribirLineas,
  escribirResultados, escribirResumen, f2 } = require('./datos');
const { todasLasRutas, mejorRuta } = require('./rutas');
const { calcularRutasSecuencial, calcularRutasConcurrente } = require('./concurrencia');
const { procesar } = require('./servicio');
const { criterios } = require('./constantes');
const { Interactivo } = require('./interactivo');
const { DatosInvalidosError } = require('./validacion');

const USO = 'Uso: node src/main.js procesar | consultar ORIGEN DESTINO | vehiculos | red | benchmark | interactivo | ventana';
const carpetaDatos = () => path.join(raizProyecto(), 'data');
const carpetaSalida = () => path.join(raizProyecto(), 'resultados');

function pedidosSinteticos(red, n) {
  const ids = red.ubicaciones().transformar((u) => u.id).ordenada((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  const tipos = criterios();
  const pedidos = new ListaEnlazada();
  for (let i = 0; i < n; i++) {
    const origen = ids.obtener((i * 7) % ids.tamano());
    let destino = ids.obtener((i * 3 + 1) % ids.tamano());
    if (origen === destino) destino = ids.obtener((i * 3 + 2) % ids.tamano());
    pedidos.agregarFinal({ origen, destino, criterio: tipos.obtener(i % 3) });
  }
  return pedidos;
}

async function cmdProcesar() {
  const red = cargarRed(carpetaDatos());
  const solicitudes = cargarSolicitudes(carpetaDatos(), red);
  const { resultados, resumen } = await procesar(red, cargarVehiculos(carpetaDatos()), solicitudes, true);
  resultados.forEach((r) => console.log(
    `${r.solicitud.id} ${r.solicitud.prioridad.padEnd(8)} ${r.estado.padEnd(9)} ${r.vehiculo.padEnd(3)} ${r.ruta ? r.ruta.texto() : '-'}`));
  console.log('\nResumen:');
  resumen.forEach((p) => console.log(`  ${p.metrica}: ${p.valor}`));
  escribirResultados(path.join(carpetaSalida(), 'resultados_javascript.csv'), resultados);
  escribirResumen(path.join(carpetaSalida(), 'resumen_javascript.csv'), resumen);
}

function cmdConsultar(origen, destino) {
  if (!origen || !destino) throw new DatosInvalidosError(USO);
  const red = cargarRed(carpetaDatos());
  console.log(`Rutas posibles ${origen} -> ${destino}:`);
  todasLasRutas(red, origen, destino).forEach((r) => console.log(
    `  ${r.texto()}  ${f2(r.distanciaKm)} km  ${f2(r.tiempoMin)} min  $${f2(r.costo)}`));
  criterios().forEach((criterio) => {
    const mejor = mejorRuta(red, origen, destino, criterio);
    console.log(`Mejor por ${criterio}: ${mejor ? mejor.texto() : 'sin ruta'}`);
  });
}

function cmdVehiculos() {
  const vehiculos = cargarVehiculos(carpetaDatos());
  ['DISPONIBLE', 'OCUPADO'].forEach((estado) =>
    console.log(`${estado}: ${vehiculos.filtrar((v) => v.estado === estado).transformar((v) => v.id)}`));
}

function cmdRed() {
  const red = cargarRed(carpetaDatos());
  console.log('Ubicaciones:');
  red.ubicaciones().forEach((u) => console.log(`  ${u.id.padEnd(4)} ${u.nombre}`));
  console.log('Conexiones:');
  red.conexiones().forEach((c) => console.log(
    `  ${c.origen.padEnd(4)} <-> ${c.destino.padEnd(4)} ${c.distanciaKm.toFixed(1).padStart(6)} km  tráfico ${c.trafico.padEnd(5)} peaje $${f2(c.peaje)}`));
}

async function medir(funcion) {
  const inicio = process.hrtime.bigint();
  await funcion();
  return Number(process.hrtime.bigint() - inicio) / 1e6;
}

async function cmdBenchmark() {
  const red = cargarRed(carpetaDatos());
  // Calentamiento para no medir el arranque en frío.
  calcularRutasSecuencial(red, pedidosSinteticos(red, 200));
  await calcularRutasConcurrente(red, pedidosSinteticos(red, 200));
  const filas = new ListaEnlazada();
  for (const n of [100, 1000, 5000]) {
    const pedidos = pedidosSinteticos(red, n);
    const seq = await medir(() => calcularRutasSecuencial(red, pedidos));
    const conc = await medir(() => calcularRutasConcurrente(red, pedidos));
    filas.agregarFinal(`javascript,${n},${seq.toFixed(1)},${conc.toFixed(1)}`);
    console.log(`n=${n}: secuencial=${seq.toFixed(1)} ms, concurrente=${conc.toFixed(1)} ms`);
  }
  escribirLineas(path.join(carpetaSalida(), 'benchmark_javascript.csv'), 'lenguaje,n,secuencial_ms,concurrente_ms', filas);
}

async function cmdInteractivo() {
  const red = cargarRed(carpetaDatos());
  await new Interactivo(red, cargarVehiculos(carpetaDatos())).ejecutar();
}

async function cmdVentana() {
  await require('./ventana').abrir();
  return 'abierta';
}

async function main(argumentos) {
  const comandos = {
    procesar: cmdProcesar, consultar: cmdConsultar, vehiculos: cmdVehiculos,
    red: cmdRed, benchmark: cmdBenchmark, interactivo: cmdInteractivo, ventana: cmdVentana,
  };
  if (!comandos[argumentos[0]]) {
    console.log(USO);
    return 1;
  }
  try {
    const resultado = await comandos[argumentos[0]](...argumentos.slice(1));
    return resultado === 'abierta' ? undefined : 0;
  } catch (error) {
    if (error instanceof DatosInvalidosError) {
      console.error(`Error de datos: ${error.message}`);
      return 2;
    }
    throw error;
  }
}

main(process.argv.slice(2)).then((codigo) => { if (codigo !== undefined) process.exitCode = codigo; });
