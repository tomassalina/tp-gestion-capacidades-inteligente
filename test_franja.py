import pytest

from franja import Franja, TipoFranja


def test_franja_guarda_nombre_y_capacidad():
    franja = Franja(TipoFranja.MANIANA, capacidad=2)
    assert franja.get_nombre() == TipoFranja.MANIANA
    assert franja.get_capacidad() == 2


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
