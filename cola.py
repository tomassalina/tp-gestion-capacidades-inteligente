class Nodo:

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

    def get_dato(self):
        return self.dato

    def get_siguiente(self):
        return self.siguiente

    def set_siguiente(self, siguiente):
        self.siguiente = siguiente


class Cola:

    def __init__(self):
        self.inicio = None
        self.fin = None
        self.cantidad = 0

    def esta_vacia(self):
        return self.inicio is None

    def encolar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.esta_vacia():
            self.inicio = nuevo_nodo
        else:
            self.fin.set_siguiente(nuevo_nodo)
        self.fin = nuevo_nodo
        self.cantidad += 1

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("La cola esta vacia")
        nodo_saliente = self.inicio
        self.inicio = nodo_saliente.get_siguiente()
        if self.inicio is None:
            self.fin = None
        self.cantidad -= 1
        return nodo_saliente.get_dato()

    def get_inicio(self):
        if self.esta_vacia():
            raise IndexError("La cola esta vacia")
        return self.inicio.get_dato()

    def recorrer(self):
        elementos = []
        actual = self.inicio
        while actual is not None:
            elementos.append(actual.get_dato())
            actual = actual.get_siguiente()
        return elementos

    def get_cantidad(self):
        return self.cantidad
