'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI)
// Modo interactivo sencillo: ver rutas, elegir una y asignar vehículo y conductor.
const readline = require('node:readline');
const { Fila } = require('./fila');
const { Solicitud } = require('./modelos');
const { DatosInvalidosError } = require('./validacion');
const { GestorFlota, cumpleSla } = require('./asignacion');
const { todasLasRutas, mejorRuta } = require('./rutas');
const { horasMaxRespuesta } = require('./constantes');
const { f2 } = require('./datos');

function tiempo(minutos) {
  const total = Math.round(minutos);
  return total >= 60 ? `${Math.floor(total / 60)} h ${total % 60} min` : `${total} min`;
}

class Interactivo {
  constructor(red, vehiculos) {
    this.red = red;
    this.vehiculos = vehiculos;
    this.flota = new GestorFlota(vehiculos);
    this.contador = 0;
    this.entrada = readline.createInterface({ input: process.stdin });
    this.lineas = this.entrada[Symbol.asyncIterator]();
  }

  /** Lee una línea; si ya no hay entrada devuelve "0" para salir. */
  async leer(mensaje) {
    process.stdout.write(mensaje);
    const siguiente = await this.lineas.next();
    return siguiente.done ? '0' : siguiente.value.trim();
  }

  nombre(id) {
    const ubicacion = this.red.ubicaciones().buscar((u) => u.id === id);
    return ubicacion ? ubicacion.nombre : id;
  }

  nombres(ruta) {
    return ruta.nodos.transformar((id) => this.nombre(id)).unir(' -> ');
  }

  /** Acepta el id (L1) o el nombre (Pachuca) y devuelve el id. */
  resolver(texto) {
    const t = texto.toLowerCase();
    const ubicacion = this.red.ubicaciones().buscar((u) => u.id.toLowerCase() === t || u.nombre.toLowerCase() === t);
    if (ubicacion === null) throw new DatosInvalidosError(`Ubicación desconocida: ${texto}`);
    return ubicacion.id;
  }

  async ejecutar() {
    let opcion = '';
    while (opcion !== '0') {
      console.log('\n1) Ver red   2) Consultar rutas y asignar viaje   3) Ver vehículos');
      console.log('4) Finalizar viaje   5) Cambiar tráfico de un tramo   0) Salir');
      opcion = await this.leer('Elige una opción: ');
      try {
        switch (opcion) {
          case '1': this.verRed(); break;
          case '2': await this.consultarYAsignar(); break;
          case '3': this.verVehiculos(); break;
          case '4': await this.finalizarViaje(); break;
          case '5': await this.cambiarTrafico(); break;
          case '0': console.log('Hasta luego.'); break;
          default: console.log('Opción no válida.');
        }
      } catch (error) {
        if (error instanceof DatosInvalidosError) console.log(`Dato inválido: ${error.message}`);
        else throw error;
      }
    }
    this.entrada.close();
  }

  verRed() {
    console.log('Ubicaciones:');
    this.red.ubicaciones().forEach((u) => console.log(`  ${u.id} ${u.nombre}`));
    console.log('Conexiones:');
    this.red.conexiones().forEach((c) => console.log(
      `  ${this.nombre(c.origen)} <-> ${this.nombre(c.destino)}  ${c.distanciaKm.toFixed(1)} km  tráfico ${c.trafico}  peaje $${c.peaje.toFixed(1)}`));
  }

  verVehiculos() {
    const mostrar = (v) => console.log(`  ${v.id} ${v.tipo} (cap. ${v.capacidad}) conductor: ${v.conductor}`);
    console.log('Disponibles:');
    this.flota.disponibles().forEach(mostrar);
    console.log('Ocupados:');
    this.flota.ocupados().forEach(mostrar);
  }

  async consultarYAsignar() {
    console.log(`Ubicaciones: ${this.red.ubicaciones().transformar((u) => u.nombre).unir(', ')}`);
    const origen = this.resolver(await this.leer('Origen (nombre o id): '));
    const destino = this.resolver(await this.leer('Destino (nombre o id): '));
    if (origen === destino) throw new DatosInvalidosError('Origen y destino deben ser distintos');

    const rutas = todasLasRutas(this.red, origen, destino).ordenada((a, b) => a.tiempoMin - b.tiempoMin);
    if (rutas.estaVacia()) {
      console.log(`No hay ruta entre ${this.nombre(origen)} y ${this.nombre(destino)}`);
      return;
    }
    const corta = mejorRuta(this.red, origen, destino, 'DISTANCIA').texto();
    const rapida = mejorRuta(this.red, origen, destino, 'TIEMPO').texto();
    const barata = mejorRuta(this.red, origen, destino, 'COSTO').texto();

    console.log('Rutas disponibles (de menor a mayor tiempo, con tráfico incluido):');
    let numero = 1;
    for (const r of rutas) {
      const marcas = (r.texto() === corta ? ' [MAS CORTA]' : '')
        + (r.texto() === rapida ? ' [MENOR TIEMPO]' : '')
        + (r.texto() === barata ? ' [MENOR COSTO]' : '');
      console.log(`  ${numero++}) ${this.nombres(r)} | ${f2(r.distanciaKm)} km | ${tiempo(r.tiempoMin)} | $${f2(r.costo)}${marcas}`);
    }

    const eleccion = Number(await this.leer('Número de ruta (0 = cancelar): '));
    if (!Number.isInteger(eleccion)) throw new DatosInvalidosError('Debes escribir un número válido');
    if (eleccion === 0) return;
    if (eleccion < 1 || eleccion > rutas.tamano()) throw new DatosInvalidosError('Número de ruta fuera de rango');
    const ruta = rutas.obtener(eleccion - 1);

    const pasajeros = await this.leer('Pasajeros: ');
    const prioridad = (await this.leer('Prioridad (CRITICA/ALTA/MEDIA/BAJA): ')).toUpperCase();
    this.contador++;
    const solicitud = Solicitud.desdeFila(Fila.de('id', `M${this.contador}`, 'origen', origen, 'destino', destino,
      'criterio', 'TIEMPO', 'pasajeros', pasajeros, 'prioridad', prioridad));

    const vehiculo = this.flota.asignar(solicitud.pasajeros);
    if (vehiculo === null) {
      console.log(`No hay vehículo disponible para ${solicitud.pasajeros} pasajeros.`);
      return;
    }
    console.log(`\nSolicitud ${solicitud.id} ASIGNADA`);
    console.log(`  Vehículo:  ${vehiculo.id} (${vehiculo.tipo})`);
    console.log(`  Conductor: ${vehiculo.conductor}`);
    console.log(`  Ruta:      ${this.nombres(ruta)}`);
    console.log(`  Tiempo estimado: ${tiempo(ruta.tiempoMin)} | Costo: $${f2(ruta.costo)}`);
    console.log(`  Tiempo máximo de respuesta (${solicitud.prioridad}): ${horasMaxRespuesta(solicitud.prioridad)} h -> `
      + `${cumpleSla(solicitud, ruta) ? 'SI cumple' : 'NO cumple'}`);
  }

  async finalizarViaje() {
    const id = (await this.leer('Id del vehículo que terminó (ej. V1): ')).toUpperCase();
    const vehiculo = this.vehiculos.buscar((v) => v.id === id);
    if (vehiculo === null) throw new DatosInvalidosError(`Vehículo no registrado: ${id}`);
    vehiculo.liberar();
    console.log(`Vehículo ${id} disponible de nuevo.`);
  }

  async cambiarTrafico() {
    const a = this.resolver(await this.leer('Ubicación A (nombre o id): '));
    const b = this.resolver(await this.leer('Ubicación B (nombre o id): '));
    const trafico = (await this.leer('Nuevo tráfico (BAJO/MEDIO/ALTO): ')).toUpperCase();
    this.red.cambiarTrafico(a, b, trafico);
    console.log('Listo. Consulta rutas de nuevo para ver el efecto.');
  }
}

module.exports = { Interactivo, tiempo };
