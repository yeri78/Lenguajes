# Responsable: Integrante 1 (modelos y validación)
"""Una fila de CSV: columnas y celdas guardadas en listas enlazadas."""
from .lista_enlazada import ListaEnlazada


class Fila:
    def __init__(self, columnas, celdas):
        self.columnas = columnas
        self.celdas = celdas

    @staticmethod
    def de(*pares):
        """Crea una fila desde pares clave, valor, clave, valor... (útil en pruebas)."""
        columnas = ListaEnlazada()
        celdas = ListaEnlazada()
        for i in range(0, len(pares) - 1, 2):
            columnas.agregar_final(pares[i])
            celdas.agregar_final(pares[i + 1])
        return Fila(columnas, celdas)

    @staticmethod
    def desde_texto(encabezado, linea):
        return Fila(ListaEnlazada.desde_iterable(encabezado.split(",")),
                    ListaEnlazada.desde_iterable(linea.split(",")))

    def obtener(self, campo):
        """Valor de la columna, o None si la columna no existe."""
        siguiente_celda = iter(self.celdas)
        for columna in self.columnas:
            celda = next(siguiente_celda, "")
            if columna.strip() == campo:
                return str(celda).strip()
        return None

    def obtener_opcional(self, campo, defecto):
        valor = self.obtener(campo)
        return defecto if valor is None or valor == "" else valor