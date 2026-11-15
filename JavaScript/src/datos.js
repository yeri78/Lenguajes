'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI). Lectura de CSV, construcción de la red y escritura de resultados.
const fs = require('node:fs');
const path = require('node:path');
const { ListaEnlazada } = require('./listaEnlazada');
const { Fila } = require('./fila');
const { Red } = require('./red');
const { Ubicacion, Conexion, Vehiculo, Solicitud } = require('./modelos');
const { DatosInvalidosError } = require('./validacion');

/** Busca hacia arriba la carpeta que contiene data/ubicaciones.csv (funciona desde cualquier subcarpeta). */
function raizProyecto() {
  let carpeta = process.cwd();
  for (let nivel = 0; nivel < 5; nivel++) {
    if (fs.existsSync(path.join(carpeta, 'data', 'ubicaciones.csv'))) return carpeta;
    carpeta = path.dirname(carpeta);
  }
  throw new DatosInvalidosError('No se encontró la carpeta data con los CSV. Ejecuta desde la carpeta del proyecto.');
}

function leerCsv(ruta) {
  let contenido;
  try {
    contenido = fs.readFileSync(ruta, 'utf-8').replace(/^\uFEFF/, '');
  } catch (error) {
    throw new DatosInvalidosError(`No se encontró el archivo: ${ruta}`);
  }
  const lineas = ListaEnlazada.desdeArreglo(contenido.split(/\r?\n/)).filtrar((l) => l.trim() !== '');
  if (lineas.estaVacia()) throw new DatosInvalidosError(`Archivo vacío: ${ruta}`);
  const encabezado = lineas.obtener(0);
  const filas = new ListaEnlazada();
  let primera = true;
  for (const linea of lineas) {
    if (primera) primera = false;
    else filas.agregarFinal(Fila.desdeTexto(encabezado, linea));
  }
  return filas;
}

function cargarRed(carpeta) {
  const red = new Red();
  leerCsv(path.join(carpeta, 'ubicaciones.csv')).forEach((f) => red.registrarUbicacion(Ubicacion.desdeFila(f)));
  leerCsv(path.join(carpeta, 'conexiones.csv')).forEach((f) => red.registrarConexion(Conexion.desdeFila(f)));
  return red;
}

function cargarVehiculos(carpeta) {
  return leerCsv(path.join(carpeta, 'vehiculos.csv')).transformar((f) => Vehiculo.desdeFila(f));
}

function cargarSolicitudes(carpeta, red) {
  const solicitudes = leerCsv(path.join(carpeta, 'solicitudes.csv')).transformar((f) => Solicitud.desdeFila(f));
  solicitudes.forEach((s) => {
    red.validarUbicacion(s.origen);
    red.validarUbicacion(s.destino);
  });
  return solicitudes;
}

const f2 = (numero) => numero.toFixed(2);

/** Escribe un CSV: encabezado y una línea de texto por elemento de la lista. */
function escribirLineas(archivo, encabezado, lineas) {
  fs.mkdirSync(path.dirname(archivo), { recursive: true });
  const cuerpo = lineas.estaVacia() ? '' : `${lineas.unir('\n')}\n`;
  fs.writeFileSync(archivo, `${encabezado}\n${cuerpo}`, 'utf-8');
}

function escribirResultados(archivo, resultados) {
  const lineas = resultados.transformar((r) => {
    const ruta = r.ruta;
    return `${r.solicitud.id},${r.solicitud.prioridad},${r.solicitud.criterio},${r.estado},${r.vehiculo},`
      + `${ruta ? ruta.texto() : '-'},${ruta ? f2(ruta.distanciaKm) : '-'},${ruta ? f2(ruta.tiempoMin) : '-'},`
      + `${ruta ? f2(ruta.costo) : '-'},${r.cumpleSla}`;
  });
  escribirLineas(archivo, 'solicitud,prioridad,criterio,estado,vehiculo,ruta,distancia_km,tiempo_min,costo,cumple_sla', lineas);
}

function escribirResumen(archivo, resumen) {
  escribirLineas(archivo, 'metrica,valor', resumen.transformar((p) => `${p.metrica},${p.valor}`));
}

module.exports = {
  raizProyecto, leerCsv, cargarRed, cargarVehiculos, cargarSolicitudes, f2,
  escribirLineas, escribirResultados, escribirResumen,
};
