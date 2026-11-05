from nodo import Nodo


class ListaEnlazada:

    def __init__(self):
        self.inicio = None

    def esta_vacia(self):
        return self.inicio is None

    def get_inicio(self):
        if self.esta_vacia():
            raise IndexError("La lista esta vacia")
        return self.inicio.get_dato()

    def insertar_inicio(self, dato):
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.set_siguiente(self.inicio)
        self.inicio = nuevo_nodo

    def insertar_despues_de(self, nodo_actual, dato):
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.set_siguiente(nodo_actual.get_siguiente())
        nodo_actual.set_siguiente(nuevo_nodo)

    def buscar(self, valor):
        return self.buscar_desde(self.inicio, valor)

    def buscar_desde(self, nodo_actual, valor):
        # caso base: se acabo la cadena (no esta) o lo encontre
        if nodo_actual is None or nodo_actual.get_dato() == valor:
            return nodo_actual
        # caso recursivo: resuelvo el mismo problema un nodo mas adelante (progreso)
        return self.buscar_desde(nodo_actual.get_siguiente(), valor)

    def eliminar(self, valor):
        self.inicio = self.eliminar_desde(self.inicio, valor)

    def eliminar_desde(self, nodo_actual, valor):
        # caso base: se acabo la cadena, no estaba
        if nodo_actual is None:
            return None
        # caso base: lo encontre, me salteo este nodo
        if nodo_actual.get_dato() == valor:
            return nodo_actual.get_siguiente()
        # caso recursivo: resuelvo el mismo problema sobre el resto de la cadena
        nodo_actual.set_siguiente(self.eliminar_desde(nodo_actual.get_siguiente(), valor))
        return nodo_actual

    def recorrer(self):
        elementos = []
        actual = self.inicio
        while actual is not None:
            elementos.append(actual.get_dato())
            actual = actual.get_siguiente()
        return elementos
