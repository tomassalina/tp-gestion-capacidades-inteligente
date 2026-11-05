from nodo import Nodo
from franja import NOMBRES_FRANJA_VALIDOS


def clave_orden(asignacion):
    return (asignacion.get_fecha(), NOMBRES_FRANJA_VALIDOS.index(asignacion.get_franja().get_nombre()))


class Agenda:

    def __init__(self):
        self.inicio = None

    def esta_vacia(self):
        return self.inicio is None

    def get_inicio(self):
        if self.esta_vacia():
            raise IndexError("La agenda esta vacia")
        return self.inicio.get_dato()

    def agregar(self, asignacion):
        nuevo_nodo = Nodo(asignacion)
        if self.esta_vacia() or clave_orden(asignacion) < clave_orden(self.inicio.get_dato()):
            nuevo_nodo.set_siguiente(self.inicio)
            self.inicio = nuevo_nodo
        else:
            self.insertar_despues(self.inicio, nuevo_nodo)

    def insertar_despues(self, nodo_actual, nuevo_nodo):
        siguiente = nodo_actual.get_siguiente()
        # caso base: no hay mas nodos, o el nuevo va justo antes del que sigue
        if siguiente is None or clave_orden(nuevo_nodo.get_dato()) < clave_orden(siguiente.get_dato()):
            nuevo_nodo.set_siguiente(siguiente)
            nodo_actual.set_siguiente(nuevo_nodo)
        else:
            # caso recursivo: el mismo problema, pero un nodo mas adelante (progreso)
            self.insertar_despues(siguiente, nuevo_nodo)

    def eliminar(self, asignacion):
        self.inicio = self.eliminar_desde(self.inicio, asignacion)

    def eliminar_desde(self, nodo_actual, asignacion):
        # caso base: se acabo la cadena, no estaba
        if nodo_actual is None:
            return None
        # caso base: lo encontre, me salteo este nodo
        if nodo_actual.get_dato() == asignacion:
            return nodo_actual.get_siguiente()
        # caso recursivo: resuelvo el mismo problema sobre el resto de la cadena
        nodo_actual.set_siguiente(self.eliminar_desde(nodo_actual.get_siguiente(), asignacion))
        return nodo_actual

    def recorrer(self):
        elementos = []
        actual = self.inicio
        while actual is not None:
            elementos.append(actual.get_dato())
            actual = actual.get_siguiente()
        return elementos
