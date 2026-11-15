'use strict';
// Responsable: Integrante 3 (red, rutas y estadísticas)
const { ListaEnlazada } = require('./listaEnlazada');

const f2 = (numero) => numero.toFixed(2);

/** Resumen estadístico. Devuelve una lista de { metrica, valor }. */
function resumir(resultados, flota) {
  const asignadas = resultados.filtrar((r) => r.estado === 'ASIGNADA');
  const conRuta = resultados.filtrar((r) => r.ruta !== null);
  const cumplen = asignadas.contar((r) => r.cumpleSla === 'SI');
  const promedio = conRuta.estaVacia() ? 0 : conRuta.sumar((r) => r.ruta.tiempoMin) / conRuta.tamano();
  const porcentaje = asignadas.estaVacia() ? 0 : (100.0 * cumplen) / asignadas.tamano();

  const resumen = new ListaEnlazada();
  const agregar = (metrica, valor) => resumen.agregarFinal({ metrica, valor: String(valor) });
  agregar('total_solicitudes', resultados.tamano());
  agregar('asignadas', asignadas.tamano());
  agregar('en_cola', resultados.contar((r) => r.estado === 'EN_COLA'));
  agregar('sin_ruta', resultados.contar((r) => r.estado === 'SIN_RUTA'));
  agregar('vehiculos_disponibles', flota.disponibles().tamano());
  agregar('vehiculos_ocupados', flota.ocupados().tamano());
  agregar('distancia_total_km', f2(asignadas.sumar((r) => r.ruta.distanciaKm)));
  agregar('costo_total', f2(asignadas.sumar((r) => r.ruta.costo)));
  agregar('tiempo_promedio_min', f2(promedio));
  agregar('cumplen_sla', cumplen);
  agregar('porcentaje_sla', f2(porcentaje));
  return resumen;
}

module.exports = { resumir };