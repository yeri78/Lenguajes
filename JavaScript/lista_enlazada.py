# Responsable: Integrante 2 (estructuras y concurrencia)
"""Lista enlazada simple (estructura 1 de 2).

Guarda ubicaciones, conexiones, vehículos, solicitudes, resultados y los caminos de las rutas.
filtrar/transformar/contar/sumar/minimo reciben funciones (orden superior).
"""


class _Nodo:
    __slots__ = ("valor", "siguiente")

    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self._cabeza = None
        self._cola = None
        self._cantidad = 0

    @staticmethod
    def desde_iterable(elementos):
        lista = ListaEnlazada()
        for elemento in elementos:
            lista.agregar_final(elemento)
        return lista

    def agregar_final(self, valor):
        nuevo = _Nodo(valor)
        if self._cabeza is None:
            self._cabeza = nuevo
        else:
            self._cola.siguiente = nuevo
        self._cola = nuevo
        self._cantidad += 1

    def agregar_inicio(self, valor):
        nuevo = _Nodo(valor)
        nuevo.siguiente = self._cabeza
        self._cabeza = nuevo
        if self._cola is None:
            self._cola = nuevo
        self._cantidad += 1

    def eliminar_ultimo(self):
        if self._cabeza is None:
            raise IndexError("La lista está vacía")
        valor = self._cola.valor
        if self._cabeza is self._cola:
            self._cabeza = None
            self._cola = None
        else:
            anterior = self._cabeza
            while anterior.siguiente is not self._cola:
                anterior = anterior.siguiente
            anterior.siguiente = None
            self._cola = anterior
        self._cantidad -= 1
        return valor

    def ultimo(self):
        if self._cola is None:
            raise IndexError("La lista está vacía")
        return self._cola.valor

    def obtener(self, indice):
        if indice < 0 or indice >= self._cantidad:
            raise IndexError(f"Índice fuera de rango: {indice}")
        actual = self._cabeza
        for _ in range(indice):
            actual = actual.siguiente
        return actual.valor

    def tamano(self):
        return self._cantidad

    def esta_vacia(self):
        return self._cantidad == 0

    def __iter__(self):
        actual = self._cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def para_cada(self, funcion):
        for valor in self:
            funcion(valor)

    def buscar(self, condicion):
        """Primer elemento que cumple la condición, o None."""
        for valor in self:
            if condicion(valor):
                return valor
        return None

    def contiene(self, condicion):
        return any(condicion(valor) for valor in self)

    def contiene_valor(self, valor):
        return self.contiene(lambda x: x == valor)

    def filtrar(self, condicion):
        resultado = ListaEnlazada()
        for valor in self:
            if condicion(valor):
                resultado.agregar_final(valor)
        return resultado

    def transformar(self, funcion):
        resultado = ListaEnlazada()
        for valor in self:
            resultado.agregar_final(funcion(valor))
        return resultado

    def contar(self, condicion):
        return self.filtrar(condicion).tamano()

    def sumar(self, funcion):
        total = 0.0
        for valor in self:
            total += funcion(valor)
        return total

    def minimo(self, comparador):
        """Elemento menor según el comparador (a, b) -> número, o None si la lista está vacía."""
        mejor = None
        hay = False
        for valor in self:
            if not hay or comparador(valor, mejor) < 0:
                mejor = valor
                hay = True
        return mejor

    def copiar(self):
        return ListaEnlazada.desde_iterable(self)

    def insertar_ordenado(self, valor, comparador):
        """Inserta manteniendo el orden; los iguales quedan después (estable)."""
        if self._cabeza is None or comparador(self._cabeza.valor, valor) > 0:
            self.agregar_inicio(valor)
            return
        actual = self._cabeza
        while actual.siguiente is not None and comparador(actual.siguiente.valor, valor) <= 0:
            actual = actual.siguiente
        nuevo = _Nodo(valor)
        nuevo.siguiente = actual.siguiente
        actual.siguiente = nuevo
        if actual is self._cola:
            self._cola = nuevo
        self._cantidad += 1

    def ordenada(self, comparador):
        resultado = ListaEnlazada()
        for valor in self:
            resultado.insertar_ordenado(valor, comparador)
        return resultado

    def unir(self, separador):
        return separador.join(str(valor) for valor in self)

    def __eq__(self, otra):
        if not isinstance(otra, ListaEnlazada) or otra._cantidad != self._cantidad:
            return False
        siguiente = iter(otra)
        return all(valor == next(siguiente) for valor in self)

    def __str__(self):
        return f"[{self.unir(', ')}]"