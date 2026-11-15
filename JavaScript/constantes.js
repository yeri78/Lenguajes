'use strict';
// Responsable: Integrante 1 (modelos y validación)
// Reglas de negocio compartidas por las tres versiones (Python, JavaScript, Java).
const { DatosInvalidosError } = require('./validacion');
const { ListaEnlazada } = require('./listaEnlazada');

const VELOCIDAD_BASE_KMH = 60.0;
const COSTO_POR_KM = 2.5;

const esTrafico = (t) => t === 'BAJO' || t === 'MEDIO' || t === 'ALTO';
const esPrioridad = (p) => p === 'CRITICA' || p === 'ALTA' || p === 'MEDIA' || p === 'BAJA';
const esCriterio = (c) => c === 'DISTANCIA' || c === 'TIEMPO' || c === 'COSTO';
const esEstadoVehiculo = (e) => e === 'DISPONIBLE' || e === 'OCUPADO';

function factorTrafico(trafico) {
  switch (trafico) {
    case 'BAJO': return 1.0;
    case 'MEDIO': return 1.3;
    case 'ALTO': return 1.7;
    default: throw new DatosInvalidosError(`Tráfico desconocido: ${trafico}`);
  }
}

/** Horas máximas de respuesta por prioridad. */
function horasMaxRespuesta(prioridad) {
  switch (prioridad) {
    case 'CRITICA': return 1;
    case 'ALTA': return 2;
    case 'MEDIA': return 8;
    case 'BAJA': return 24;
    default: throw new DatosInvalidosError(`Prioridad desconocida: ${prioridad}`);
  }
}

/** Menor número = se atiende primero. */
function ordenPrioridad(prioridad) {
  switch (prioridad) {
    case 'CRITICA': return 0;
    case 'ALTA': return 1;
    case 'MEDIA': return 2;
    case 'BAJA': return 3;
    default: throw new DatosInvalidosError(`Prioridad desconocida: ${prioridad}`);
  }
}

function criterios() {
  return ListaEnlazada.desdeArreglo(['DISTANCIA', 'TIEMPO', 'COSTO']);
}

module.exports = {
  VELOCIDAD_BASE_KMH, COSTO_POR_KM, esTrafico, esPrioridad, esCriterio, esEstadoVehiculo,
  factorTrafico, horasMaxRespuesta, ordenPrioridad, criterios,
};