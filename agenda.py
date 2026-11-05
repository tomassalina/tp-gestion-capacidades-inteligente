from lista_enlazada import ListaEnlazada
from franja import NOMBRES_FRANJA_VALIDOS


def clave_orden(asignacion):
    return (asignacion.get_fecha(), NOMBRES_FRANJA_VALIDOS.index(asignacion.get_franja().get_nombre()))


class Agenda(ListaEnlazada):

    def agregar(self, asignacion):
        if self.esta_vacia() or clave_orden(asignacion) < clave_orden(self.inicio.get_dato()):
            self.insertar_inicio(asignacion)
        else:
            self.insertar_ordenado_despues(self.inicio, asignacion)

    def insertar_ordenado_despues(self, nodo_actual, asignacion):
        siguiente = nodo_actual.get_siguiente()
        # caso base: no hay mas nodos, o el nuevo va justo antes del que sigue
        if siguiente is None or clave_orden(asignacion) < clave_orden(siguiente.get_dato()):
            self.insertar_despues_de(nodo_actual, asignacion)
        else:
            # caso recursivo: el mismo problema, pero un nodo mas adelante (progreso)
            self.insertar_ordenado_despues(siguiente, asignacion)
