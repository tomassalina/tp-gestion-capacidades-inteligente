class Nodo:

    def __init__(self, dato):
        self._dato = dato
        self._siguiente = None

    def get_dato(self):
        return self._dato

    def get_siguiente(self):
        return self._siguiente

    def set_siguiente(self, siguiente):
        self._siguiente = siguiente


class Cola:

    def __init__(self):
        self._inicio = None
        self._fin = None
        self._cantidad = 0

    def esta_vacia(self):
        return self._inicio is None

    def encolar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.esta_vacia():
            self._inicio = nuevo_nodo
        else:
            self._fin.set_siguiente(nuevo_nodo)
        self._fin = nuevo_nodo
        self._cantidad += 1

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("La cola esta vacia")
        nodo_saliente = self._inicio
        self._inicio = nodo_saliente.get_siguiente()
        if self._inicio is None:
            self._fin = None
        self._cantidad -= 1
        return nodo_saliente.get_dato()

    def recorrer(self):
        elementos = []
        actual = self._inicio
        while actual is not None:
            elementos.append(actual.get_dato())
            actual = actual.get_siguiente()
        return elementos

    def __len__(self):
        return self._cantidad


def test_cola_respeta_orden_fifo():
    cola = Cola()
    cola.encolar(1)
    cola.encolar(2)
    cola.encolar(3)
    assert cola.desencolar() == 1
    assert cola.desencolar() == 2
    assert cola.desencolar() == 3


def test_cola_esta_vacia_antes_y_despues():
    cola = Cola()
    assert cola.esta_vacia()
    cola.encolar("x")
    assert not cola.esta_vacia()
    cola.desencolar()
    assert cola.esta_vacia()


def test_desencolar_cola_vacia_lanza_index_error():
    import pytest

    cola = Cola()
    with pytest.raises(IndexError):
        cola.desencolar()


def test_len_y_recorrer_reflejan_los_elementos_encolados():
    cola = Cola()
    cola.encolar("a")
    cola.encolar("b")
    cola.encolar("c")
    assert len(cola) == 3
    assert cola.recorrer() == ["a", "b", "c"]
