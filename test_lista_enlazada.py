import pytest

from lista_enlazada import ListaEnlazada


def test_lista_vacia_al_crearse():
    lista = ListaEnlazada()
    assert lista.esta_vacia()
    assert lista.recorrer() == []


def test_insertar_inicio_varias_veces_queda_en_orden_inverso():
    lista = ListaEnlazada()
    lista.insertar_inicio(1)
    lista.insertar_inicio(2)
    lista.insertar_inicio(3)
    assert lista.recorrer() == [3, 2, 1]
    assert lista.get_inicio() == 3


def test_insertar_despues_de_un_nodo():
    lista = ListaEnlazada()
    lista.insertar_inicio("a")
    lista.insertar_despues_de(lista.inicio, "b")
    assert lista.recorrer() == ["a", "b"]


def test_buscar_devuelve_el_nodo_con_el_valor():
    lista = ListaEnlazada()
    lista.insertar_inicio(3)
    lista.insertar_inicio(2)
    lista.insertar_inicio(1)
    nodo = lista.buscar(2)
    assert nodo.get_dato() == 2


def test_buscar_algo_que_no_esta_devuelve_none():
    lista = ListaEnlazada()
    lista.insertar_inicio(1)
    assert lista.buscar(99) is None


def test_eliminar_el_primero():
    lista = ListaEnlazada()
    lista.insertar_inicio(2)
    lista.insertar_inicio(1)
    lista.eliminar(1)
    assert lista.recorrer() == [2]


def test_eliminar_del_medio_no_rompe_el_resto():
    lista = ListaEnlazada()
    lista.insertar_inicio(3)
    lista.insertar_inicio(2)
    lista.insertar_inicio(1)
    lista.eliminar(2)
    assert lista.recorrer() == [1, 3]


def test_get_inicio_en_lista_vacia_lanza_index_error():
    lista = ListaEnlazada()
    with pytest.raises(IndexError):
        lista.get_inicio()
