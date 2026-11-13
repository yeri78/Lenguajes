'use strict';
// Responsable: Integrante 1 (modelos y validación)
const { DatosInvalidosError, requerirTexto, requerirNumero, requerirEntero, requerirOpcion } = require('./validacion');
const C = require('./constantes');

class Ubicacion {
  constructor(id, nombre, x = 0, y = 0) {
    Object.assign(this, { id, nombre, x, y });
  }

  static desdeFila(fila) {
    return new Ubicacion(requerirTexto(fila, 'id'), requerirTexto(fila, 'nombre'),
      Number(fila.obtenerOpcional('x', '0')), Number(fila.obtenerOpcional('y', '0')));
  }
}

/** Tramo entre dos ubicaciones (se usa en ambos sentidos). */
class Conexion {
  constructor(origen, destino, distanciaKm, trafico, peaje) {
    Object.assign(this, { origen, destino, distanciaKm, trafico, peaje });
  }

  static desdeFila(fila) {
    const origen = requerirTexto(fila, 'origen');
    const destino = requerirTexto(fila, 'destino');
    if (origen === destino) {
      throw new DatosInvalidosError('Una conexión no puede unir una ubicación consigo misma');
    }
    return new Conexion(origen, destino,
      requerirNumero(fila, 'distancia_km', true),
      requerirOpcion(fila, 'trafico', C.esTrafico, 'BAJO, MEDIO, ALTO'),
      requerirNumero(fila, 'peaje', false));
  }

  invertida() {
    return new Conexion(this.destino, this.origen, this.distanciaKm, this.trafico, this.peaje);
  }

  tiempoMin() {
    return this.distanciaKm / C.VELOCIDAD_BASE_KMH * 60.0 * C.factorTrafico(this.trafico);
  }

  costo() {
    return this.distanciaKm * C.COSTO_POR_KM + this.peaje;
  }

  peso(criterio) {
    switch (criterio) {
      case 'DISTANCIA': return this.distanciaKm;
      case 'TIEMPO': return this.tiempoMin();
      case 'COSTO': return this.costo();
      default: throw new DatosInvalidosError(`Criterio desconocido: ${criterio}`);
    }
  }
}

class Vehiculo {
  constructor(id, tipo, capacidad, estado = 'DISPONIBLE', conductor = 'Sin conductor') {
    Object.assign(this, { id, tipo, capacidad, estado, conductor });
  }

  static desdeFila(fila) {
    return new Vehiculo(requerirTexto(fila, 'id'), requerirTexto(fila, 'tipo'),
      requerirEntero(fila, 'capacidad'),
      requerirOpcion(fila, 'estado', C.esEstadoVehiculo, 'DISPONIBLE, OCUPADO'),
      fila.obtenerOpcional('conductor', 'Sin conductor'));
  }

  get disponible() {
    return this.estado === 'DISPONIBLE';
  }

  ocupar() {
    this.estado = 'OCUPADO';
  }

  liberar() {
    this.estado = 'DISPONIBLE';
  }
}

class Solicitud {
  constructor(id, origen, destino, prioridad, criterio, pasajeros) {
    Object.assign(this, { id, origen, destino, prioridad, criterio, pasajeros });
  }

  static desdeFila(fila) {
    const origen = requerirTexto(fila, 'origen');
    const destino = requerirTexto(fila, 'destino');
    if (origen === destino) {
      throw new DatosInvalidosError('Origen y destino de la solicitud deben ser distintos');
    }
    return new Solicitud(requerirTexto(fila, 'id'), origen, destino,
      requerirOpcion(fila, 'prioridad', C.esPrioridad, 'CRITICA, ALTA, MEDIA, BAJA'),
      requerirOpcion(fila, 'criterio', C.esCriterio, 'DISTANCIA, TIEMPO, COSTO'),
      requerirEntero(fila, 'pasajeros'));
  }
}

module.exports = { Ubicacion, Conexion, Vehiculo, Solicitud };