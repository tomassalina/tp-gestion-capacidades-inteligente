import pytest

from cola import Cola


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
