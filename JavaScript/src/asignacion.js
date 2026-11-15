'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI)
// Gestión de flota y asignación de solicitudes por prioridad.
const { ColaPrioridad } = require('./colaPrioridad');
const { ListaEnlazada } = require('./listaEnlazada');
const { ResultadoSolicitud } = require('./resultadoSolicitud');
const { horasMaxRespuesta, ordenPrioridad } = require('./constantes');

const compararTexto = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

/** Críticas primero; a igual prioridad, por id. */
const POR_PRIORIDAD = (a, b) =>
  (ordenPrioridad(a.prioridad) - ordenPrioridad(b.prioridad)) || compararTexto(a.id, b.id);

class GestorFlota {
  constructor(vehiculos) {
    this.vehiculos = vehiculos;
  }

  disponibles() {
    return this.vehiculos.filtrar((v) => v.disponible);
  }

  ocupados() {
    return this.vehiculos.filtrar((v) => !v.disponible);
  }

  /** Elige el vehículo disponible más pequeño que alcance (best-fit), lo marca ocupado y lo devuelve (o null). */
  asignar(pasajeros) {
    const elegido = this.disponibles()
      .filtrar((v) => v.capacidad >= pasajeros)
      .minimo((a, b) => (a.capacidad - b.capacidad) || compararTexto(a.id, b.id));
    if (elegido !== null) elegido.ocupar();
    return elegido;
  }
}

function ordenarPorPrioridad(solicitudes) {
  const cola = new ColaPrioridad(POR_PRIORIDAD);
  solicitudes.forEach((s) => cola.encolar(s));
  const ordenadas = new ListaEnlazada();
  while (!cola.estaVacia()) ordenadas.agregarFinal(cola.desencolar());
  return ordenadas;
}

function cumpleSla(solicitud, ruta) {
  return ruta.tiempoMin <= horasMaxRespuesta(solicitud.prioridad) * 60;
}

/** pendientes: lista de { solicitud, ruta }. Sin camino -> SIN_RUTA; sin vehículo disponible -> EN_COLA. */
function asignarSolicitudes(pendientes, flota) {
  const cola = new ColaPrioridad((a, b) => POR_PRIORIDAD(a.solicitud, b.solicitud));
  pendientes.forEach((p) => cola.encolar(p));
  const resultados = new ListaEnlazada();
  while (!cola.estaVacia()) {
    const { solicitud, ruta } = cola.desencolar();
    if (ruta === null) {
      resultados.agregarFinal(new ResultadoSolicitud(solicitud, 'SIN_RUTA'));
      continue;
    }
    const vehiculo = flota.asignar(solicitud.pasajeros);
    if (vehiculo === null) {
      resultados.agregarFinal(new ResultadoSolicitud(solicitud, 'EN_COLA', ruta));
    } else {
      resultados.agregarFinal(new ResultadoSolicitud(solicitud, 'ASIGNADA', ruta, vehiculo.id,
        cumpleSla(solicitud, ruta) ? 'SI' : 'NO'));
    }
  }
  return resultados;
}

module.exports = { POR_PRIORIDAD, GestorFlota, ordenarPorPrioridad, cumpleSla, asignarSolicitudes };
