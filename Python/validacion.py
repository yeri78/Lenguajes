# Responsable: Integrante 1 (modelos y validación)
"""Excepción propia y funciones de validación compartidas por los modelos."""
import math


class DatosInvalidosError(ValueError):
    """Se lanza cuando un dato de entrada no cumple las reglas del negocio."""


def requerir_texto(fila, campo):
    valor = fila.obtener(campo)
    if valor is None or valor.strip() == "":
        raise DatosInvalidosError(f"El campo '{campo}' no puede estar vacío")
    return valor.strip()


def requerir_numero(fila, campo, estrictamente_positivo):
    """estrictamente_positivo=True exige > 0; False exige >= 0."""
    texto = requerir_texto(fila, campo)
    try:
        numero = float(texto)
    except ValueError:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico: {texto}")
    if not math.isfinite(numero):
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico: {texto}")
    if estrictamente_positivo and numero <= 0:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser mayor que cero: {texto}")
    if not estrictamente_positivo and numero < 0:
        raise DatosInvalidosError(f"El campo '{campo}' no puede ser negativo: {texto}")
    return numero


def requerir_entero(fila, campo):
    numero = requerir_numero(fila, campo, True)
    if numero != int(numero):
        raise DatosInvalidosError(f"El campo '{campo}' debe ser entero: {numero}")
    return int(numero)


def requerir_opcion(fila, campo, es_valida, opciones):
    """es_valida es una función que decide si el valor está permitido."""
    texto = requerir_texto(fila, campo).upper()
    if not es_valida(texto):
        raise DatosInvalidosError(f"'{campo}' inválido: {texto}. Opciones: {opciones}")
    return texto