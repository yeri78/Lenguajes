'use strict';
// Responsable: Integrante 4 (asignación, datos y CLI)
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { once } = require('node:events');
const { Fila } = require('./fila');
const { raizProyecto, cargarRed, cargarVehiculos, cargarSolicitudes, f2 } = require('./datos');
const { todasLasRutas, mejorRuta } = require('./rutas');
const { procesar } = require('./servicio');
const { GestorFlota, cumpleSla } = require('./asignacion');
const { Solicitud } = require('./modelos');
const { DatosInvalidosError } = require('./validacion');
const { horasMaxRespuesta } = require('./constantes');

const HOST = '127.0.0.1';
const LIMITE_CUERPO = 1024 * 1024;
const rutaHtml = path.join(__dirname, 'ventana.html');

function tiempo(minutos) {
  const total = Math.round(minutos);
  return total >= 60 ? `${Math.floor(total / 60)} h ${total % 60} min` : `${total} min`;
}

function respuesta(res, codigo, cuerpo, tipo = 'application/json; charset=utf-8') {
  res.writeHead(codigo, {
    'Content-Type': tipo,
    'X-Content-Type-Options': 'nosniff',
    'Cache-Control': 'no-store',
  });
  res.end(tipo.startsWith('application/json') ? JSON.stringify(cuerpo) : cuerpo);
}

async function leerCuerpo(req) {
  const bloques = [];
  let total = 0;
  for await (const bloque of req) {
    total += bloque.length;
    if (total > LIMITE_CUERPO) {
      throw new DatosInvalidosError('La solicitud es demasiado grande');
    }
    bloques.push(bloque);
  }
  try {
    return JSON.parse(Buffer.concat(bloques).toString('utf8'));
  } catch {
    throw new DatosInvalidosError('El cuerpo debe contener JSON válido');
  }
}

function crearServidor() {
  const carpetaDatos = path.join(raizProyecto(), 'data');
  const red = cargarRed(carpetaDatos);
  const vehiculos = cargarVehiculos(carpetaDatos);
  const flota = new GestorFlota(vehiculos);
  let rutas = null;
  let origen = '';
  let destino = '';
  let contador = 0;

  async function manejar(req, res) {
    const url = new URL(req.url, `http://${HOST}`);
    if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/ventana.html')) {
      respuesta(res, 200, fs.readFileSync(rutaHtml, 'utf8'), 'text/html; charset=utf-8');
      return;
    }
    if (url.pathname === '/api/estado' && req.method === 'GET') {
      respuesta(res, 200, {
        ubicaciones: red.ubicaciones().transformar((u) => ({ id: u.id, nombre: u.nombre })).aArreglo(),
        disponibles: flota.disponibles().transformar((v) => ({
          id: v.id, tipo: v.tipo, capacidad: v.capacidad, conductor: v.conductor,
        })).aArreglo(),
        ocupados: flota.ocupados().transformar((v) => ({
          id: v.id, tipo: v.tipo, capacidad: v.capacidad, conductor: v.conductor,
        })).aArreglo(),
        conexiones: red.conexiones().transformar((c) => ({
          origen: c.origen, destino: c.destino, desde: c.origen, hasta: c.destino,
          km: f2(c.distanciaKm), trafico: c.trafico, peaje: f2(c.peaje),
        })).aArreglo(),
      });
      return;
    }

    if (!url.pathname.startsWith('/api/')) {
      respuesta(res, 404, { error: 'No encontrado' });
      return;
    }
    if (req.method !== 'POST') {
      respuesta(res, 405, { error: 'Método no permitido' });
      return;
    }

    const cuerpo = await leerCuerpo(req);
    if (cuerpo === null || typeof cuerpo !== 'object' || Array.isArray(cuerpo)) {
      throw new DatosInvalidosError('El cuerpo debe ser un objeto JSON');
    }
    if (url.pathname === '/api/rutas') {
      if (!cuerpo.origen || !cuerpo.destino || cuerpo.origen === cuerpo.destino) {
        throw new DatosInvalidosError('Elige dos ubicaciones distintas');
      }
      rutas = todasLasRutas(red, cuerpo.origen, cuerpo.destino)
        .ordenada((a, b) => a.tiempoMin - b.tiempoMin);
      origen = cuerpo.origen;
      destino = cuerpo.destino;
      if (rutas.estaVacia()) {
        respuesta(res, 200, { rutas: [] });
        return;
      }
      const corta = mejorRuta(red, origen, destino, 'DISTANCIA');
      const rapida = mejorRuta(red, origen, destino, 'TIEMPO');
      const barata = mejorRuta(red, origen, destino, 'COSTO');
      let numero = 0;
      respuesta(res, 200, {
        rutas: rutas.transformar((ruta) => {
          numero++;
          const marcas = [
            ruta.texto() === corta.texto() ? 'MAS CORTA' : '',
            ruta.texto() === rapida.texto() ? 'MENOR TIEMPO' : '',
            ruta.texto() === barata.texto() ? 'MENOR COSTO' : '',
          ].filter(Boolean).join(' ');
          return {
            numero,
            ruta: ruta.nodos.transformar((id) =>
              red.ubicaciones().buscar((u) => u.id === id).nombre).unir(' -> '),
            km: f2(ruta.distanciaKm),
            tiempo: tiempo(ruta.tiempoMin),
            costo: `$${f2(ruta.costo)}`,
            marcas,
          };
        }).aArreglo(),
      });
      return;
    }

    if (url.pathname === '/api/asignar') {
      if (rutas === null) throw new DatosInvalidosError('Primero busca rutas');
      const numero = Number(cuerpo.numero);
      if (!Number.isInteger(numero) || numero < 1 || numero > rutas.tamano()) {
        throw new DatosInvalidosError('Selecciona una ruta de la tabla');
      }
      const solicitud = Solicitud.desdeFila(Fila.de(
        'id', `M${contador + 1}`, 'origen', origen, 'destino', destino,
        'criterio', 'TIEMPO', 'pasajeros', String(cuerpo.pasajeros ?? ''),
        'prioridad', String(cuerpo.prioridad ?? ''),
      ));
      contador++;
      const ruta = rutas.obtener(numero - 1);
      const vehiculo = flota.asignar(solicitud.pasajeros);
      if (vehiculo === null) {
        respuesta(res, 200, { texto: `No hay vehículo disponible para ${solicitud.pasajeros} pasajeros.` });
        return;
      }
      respuesta(res, 200, {
        texto: `Solicitud ${solicitud.id} ASIGNADA\n`
          + `  Vehículo:  ${vehiculo.id} (${vehiculo.tipo})\n`
          + `  Conductor: ${vehiculo.conductor}\n`
          + `  Ruta:      ${ruta.nodos.transformar((id) =>
            red.ubicaciones().buscar((u) => u.id === id).nombre).unir(' -> ')}\n`
          + `  Tiempo estimado: ${tiempo(ruta.tiempoMin)} | Costo: $${f2(ruta.costo)}\n`
          + `  Tiempo máximo de respuesta (${solicitud.prioridad}): `
          + `${horasMaxRespuesta(solicitud.prioridad)} h -> `
          + `${cumpleSla(solicitud, ruta) ? 'SI cumple' : 'NO cumple'}`,
      });
      return;
    }

    if (url.pathname === '/api/finalizar') {
      const vehiculo = vehiculos.buscar((v) => v.id === cuerpo.id);
      if (vehiculo === null) throw new DatosInvalidosError(`Vehículo no registrado: ${cuerpo.id}`);
      vehiculo.liberar();
      respuesta(res, 200, { correcto: true });
      return;
    }

    if (url.pathname === '/api/trafico') {
      red.cambiarTrafico(cuerpo.origen, cuerpo.destino, cuerpo.trafico);
      respuesta(res, 200, { correcto: true });
      return;
    }

    if (url.pathname === '/api/procesar') {
      const redNueva = cargarRed(carpetaDatos);
      const solicitudes = cargarSolicitudes(carpetaDatos, redNueva);
      const salida = await procesar(redNueva, cargarVehiculos(carpetaDatos), solicitudes, true);
      respuesta(res, 200, {
        filas: salida.resultados.transformar((r) => ({
          id: r.solicitud.id, prioridad: r.solicitud.prioridad, estado: r.estado,
          vehiculo: r.vehiculo, sla: r.cumpleSla, ruta: r.ruta ? r.ruta.texto() : '-',
        })).aArreglo(),
        resumen: salida.resumen.transformar((p) => `${p.metrica}: ${p.valor}`).aArreglo(),
      });
      return;
    }
    respuesta(res, 404, { error: 'No encontrado' });
  }

  return http.createServer((req, res) => {
    manejar(req, res).catch((error) => {
      if (res.headersSent) {
        res.destroy(error);
      } else if (error instanceof DatosInvalidosError) {
        respuesta(res, 400, { error: error.message });
      } else {
        console.error('Error al atender la ventana:', error);
        respuesta(res, 500, { error: 'Ocurrió un error interno al procesar la solicitud' });
      }
    });
  });
}

function abrirNavegador(url) {
  const comando = process.platform === 'win32' ? 'rundll32.exe'
    : process.platform === 'darwin' ? 'open' : 'xdg-open';
  const argumentos = process.platform === 'win32' ? ['url.dll,FileProtocolHandler', url] : [url];
  execFile(comando, argumentos, (error) => {
    if (error) console.error(`No se pudo abrir el navegador automáticamente. Abre ${url} manualmente.`);
  });
}

async function abrir() {
  const servidor = crearServidor();
  const puerto = Number(process.env.PORT || 3000);
  servidor.listen(puerto, HOST);
  await once(servidor, 'listening');
  const url = `http://${HOST}:${servidor.address().port}/`;
  console.log(`Ventana JavaScript disponible en ${url} (Ctrl+C para cerrar).`);
  abrirNavegador(url);
}

module.exports = { crearServidor, abrir };
