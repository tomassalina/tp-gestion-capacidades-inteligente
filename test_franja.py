import pytest

from franja import Franja, TipoFranja


def test_franja_tiene_lugar_inicialmente():
    franja = Franja(TipoFranja.MANIANA, capacidad=2)
    assert franja.tiene_lugar()


def test_franja_nombre_fuera_del_tipo_lanza_value_error():
    with pytest.raises(ValueError):
        Franja("Madrugada", capacidad=2)


def test_franja_tipos_o_valores_invalidos_lanza_error():
    with pytest.raises(TypeError):
        Franja(123, capacidad=2)
    with pytest.raises(TypeError):
        Franja("Manana", capacidad="2")
    with pytest.raises(ValueError):
        Franja("Manana", capacidad=0)


def test_franja_se_completa_al_ocupar_todo_el_lugar():
    franja = Franja("Manana", capacidad=1)
    franja.ocupar_lugar()
    assert not franja.tiene_lugar()
    assert franja.get_trabajadores_asignados() == 1


def test_franja_libera_lugar():
    franja = Franja("Manana", capacidad=1)
    franja.ocupar_lugar()
    franja.liberar_lugar()
    assert franja.tiene_lugar()
    assert franja.get_trabajadores_asignados() == 0
