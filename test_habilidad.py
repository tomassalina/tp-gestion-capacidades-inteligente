import pytest

from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad


def test_habilidad_igualdad_por_nombre():
    habilidad_a = Habilidad("Soldadura")
    habilidad_b = Habilidad("Soldadura")
    habilidad_c = Habilidad("Electricidad")
    assert habilidad_a == habilidad_b
    assert habilidad_a != habilidad_c


def test_habilidad_tipo_o_valor_invalido_lanza_error():
    with pytest.raises(TypeError):
        Habilidad(123)
    with pytest.raises(ValueError):
        Habilidad("   ")


def test_habilidad_de_trabajador_cumple_nivel_minimo():
    habilidad = Habilidad("Soldadura")
    propia = HabilidadDeTrabajador(habilidad, NivelHabilidad.INTERMEDIO)
    assert propia.cumple_nivel_minimo(NivelHabilidad.BASICO)
    assert propia.cumple_nivel_minimo(NivelHabilidad.INTERMEDIO)
    assert not propia.cumple_nivel_minimo(NivelHabilidad.AVANZADO)


def test_habilidad_de_trabajador_tipo_o_nivel_invalido_lanza_error():
    habilidad = Habilidad("Soldadura")
    with pytest.raises(TypeError):
        HabilidadDeTrabajador("no es habilidad", NivelHabilidad.BASICO)
    with pytest.raises(ValueError):
        HabilidadDeTrabajador(habilidad, 99)


def test_habilidad_requerida_getters():
    habilidad = Habilidad("Soldadura")
    requerida = HabilidadRequerida(habilidad, NivelHabilidad.AVANZADO)
    assert requerida.get_habilidad() == habilidad
    assert requerida.get_nivel_minimo() == NivelHabilidad.AVANZADO


def test_habilidad_requerida_tipo_o_nivel_invalido_lanza_error():
    habilidad = Habilidad("Soldadura")
    with pytest.raises(TypeError):
        HabilidadRequerida("no es habilidad", NivelHabilidad.BASICO)
    with pytest.raises(ValueError):
        HabilidadRequerida(habilidad, 99)
