from nodo import Nodo


def test_nodo_guarda_el_dato():
    nodo = Nodo(5)
    assert nodo.get_dato() == 5
    assert nodo.get_siguiente() is None


def test_nodo_set_siguiente_enlaza_con_otro_nodo():
    primero = Nodo("a")
    segundo = Nodo("b")
    primero.set_siguiente(segundo)
    assert primero.get_siguiente() is segundo
    assert primero.get_siguiente().get_dato() == "b"
