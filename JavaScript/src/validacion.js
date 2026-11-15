'use strict';
// Responsable: Integrante 1 (modelos y validación)

/** Se lanza cuando un dato de entrada no cumple las reglas del negocio. */
class DatosInvalidosError extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = 'DatosInvalidosError';
  }
}

function requerirTexto(fila, campo) {
  const valor = fila.obtener(campo);
  if (valor === null || valor.trim() === '') {
    throw new DatosInvalidosError(`El campo '${campo}' no puede estar vacío`);
  }
  return valor.trim();
}

/** estrictamentePositivo=true exige > 0; false exige >= 0. */
function requerirNumero(fila, campo, estrictamentePositivo) {
  const texto = requerirTexto(fila, campo);
  const numero = Number(texto);
  if (!Number.isFinite(numero)) {
    throw new DatosInvalidosError(`El campo '${campo}' debe ser numérico: ${texto}`);
  }
  if (estrictamentePositivo && numero <= 0) {
    throw new DatosInvalidosError(`El campo '${campo}' debe ser mayor que cero: ${texto}`);
  }
  if (!estrictamentePositivo && numero < 0) {
    throw new DatosInvalidosError(`El campo '${campo}' no puede ser negativo: ${texto}`);
  }
  return numero;
}

function requerirEntero(fila, campo) {
  const numero = requerirNumero(fila, campo, true);
  if (!Number.isInteger(numero)) {
    throw new DatosInvalidosError(`El campo '${campo}' debe ser entero: ${numero}`);
  }
  return numero;
}

/** Recibe una función (esValida) que decide si el valor es permitido. */
function requerirOpcion(fila, campo, esValida, opciones) {
  const texto = requerirTexto(fila, campo).toUpperCase();
  if (!esValida(texto)) {
    throw new DatosInvalidosError(`'${campo}' inválido: ${texto}. Opciones: ${opciones}`);
  }
  return texto;
}

module.exports = { DatosInvalidosError, requerirTexto, requerirNumero, requerirEntero, requerirOpcion };