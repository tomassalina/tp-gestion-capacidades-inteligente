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
