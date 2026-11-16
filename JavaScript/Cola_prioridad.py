# Responsable: Integrante 2 (estructuras y concurrencia)
"""Cola de prioridad como lista enlazada ordenada (estructura 2 de 2).

Atiende solicitudes (críticas primero) y sirve de frontera en la búsqueda de rutas.
"""


class _Nodo:
    __slots__ = ("valor", "siguiente")

    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None


class ColaPrioridad:
    def __init__(self, comparador):
        self._comparador = comparador
        self._frente = None
        self._cantidad = 0

    def encolar(self, valor):
        """Inserta en su posición; ante empate queda después de los existentes (FIFO)."""
        nuevo = _Nodo(valor)
        if self._frente is None or self._comparador(self._frente.valor, valor) > 0:
            nuevo.siguiente = self._frente
            self._frente = nuevo
        else:
            actual = self._frente
            while actual.siguiente is not None and self._comparador(actual.siguiente.valor, valor) <= 0:
                actual = actual.siguiente
            nuevo.siguiente = actual.siguiente
            actual.siguiente = nuevo
        self._cantidad += 1

    def desencolar(self):
        if self._frente is None:
            raise IndexError("La cola está vacía")
        valor = self._frente.valor
        self._frente = self._frente.siguiente
        self._cantidad -= 1
        return valor

    def esta_vacia(self):
        return self._frente is None

    def tamano(self):
        return self._cantidad