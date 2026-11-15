'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI)

/** estado: ASIGNADA | EN_COLA | SIN_RUTA. ruta puede ser null. */
class ResultadoSolicitud {
  constructor(solicitud, estado, ruta = null, vehiculo = '-', cumpleSla = '-') {
    Object.assign(this, { solicitud, estado, ruta, vehiculo, cumpleSla });
  }
}

module.exports = { ResultadoSolicitud };
