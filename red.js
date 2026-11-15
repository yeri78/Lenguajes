'use strict';
// Responsable: Integrante 3 (red, rutas y estadísticas)
const { ListaEnlazada } = require('./listaEnlazada');
const { Conexion } = require('./modelos');
const { DatosInvalidosError } = require('./validacion');
const { esTrafico } = require('./constantes');

/**
 * Red de transporte guardada en dos listas enlazadas: ubicaciones y conexiones.
 * Cada conexión se guarda una sola vez y se puede recorrer en ambos sentidos.
 */
class Red {
  constructor() {
    this.listaUbicaciones = new ListaEnlazada();
    this.listaConexiones = new ListaEnlazada();
  }

  registrarUbicacion(ubicacion) {
    if (this.existe(ubicacion.id)) throw new DatosInvalidosError(`Ubicación duplicada: ${ubicacion.id}`);
    this.listaUbicaciones.agregarFinal(ubicacion);
  }

  registrarConexion(conexion) {
    this.validarUbicacion(conexion.origen);
    this.validarUbicacion(conexion.destino);
    if (this.buscarConexion(conexion.origen, conexion.destino) !== null) {
      throw new DatosInvalidosError(`Conexión duplicada: ${conexion.origen}-${conexion.destino}`);
    }
    this.listaConexiones.agregarFinal(conexion);
  }

  existe(id) {
    return this.listaUbicaciones.contiene((u) => u.id === id);
  }

  validarUbicacion(id) {
    if (!this.existe(id)) throw new DatosInvalidosError(`Ubicación desconocida: ${id}`);
  }

  /** Conexión entre a y b orientada de a hacia b, o null si no existe. */
  buscarConexion(a, b) {
    for (const c of this.listaConexiones) {
      if (c.origen === a && c.destino === b) return c;
      if (c.origen === b && c.destino === a) return c.invertida();
    }
    return null;
  }

  /** Conexiones que salen de la ubicación, todas orientadas desde ella. */
  vecinos(id) {
    const salientes = new ListaEnlazada();
    for (const c of this.listaConexiones) {
      if (c.origen === id) salientes.agregarFinal(c);
      else if (c.destino === id) salientes.agregarFinal(c.invertida());
    }
    return salientes;
  }

  /** Cambia el nivel de tráfico de un tramo (en ambos sentidos). */
  cambiarTrafico(a, b, nuevoTrafico) {
    if (!esTrafico(nuevoTrafico)) {
      throw new DatosInvalidosError(`Tráfico inválido: ${nuevoTrafico}. Opciones: BAJO, MEDIO, ALTO`);
    }
    if (this.buscarConexion(a, b) === null) {
      throw new DatosInvalidosError(`No existe conexión entre ${a} y ${b}`);
    }
    const unen = (c) => (c.origen === a && c.destino === b) || (c.origen === b && c.destino === a);
    this.listaConexiones = this.listaConexiones.transformar((c) =>
      (unen(c) ? new Conexion(c.origen, c.destino, c.distanciaKm, nuevoTrafico, c.peaje) : c));
  }

  ubicaciones() {
    return this.listaUbicaciones;
  }

  conexiones() {
    return this.listaConexiones;
  }
}

module.exports = { Red };