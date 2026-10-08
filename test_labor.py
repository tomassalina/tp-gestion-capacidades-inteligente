import pytest

from area_de_trabajo import AreaDeTrabajo
from labor import Labor


def test_labor_duracion_invalida_lanza_value_error():
    with pytest.raises(ValueError):
        Labor(1, "Titulo", "Descripcion", 0, [], [], None)


def test_labor_se_crea_correctamente():
    area = AreaDeTrabajo("Cocina", [], [])
    labor = Labor(1, "Preparar almuerzo", "Cocinar el menu", 4, [], ["Carnet"], area)
    assert labor.get_titulo() == "Preparar almuerzo"
    assert labor.get_duracion_horas() == 4
    assert labor.get_area() == area


def test_labor_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    area = AreaDeTrabajo("Cocina", [], [])
    with pytest.raises(TypeError):
        Labor(1, "Titulo", "Descripcion", 4, ["no es habilidad requerida"], [], area)


def test_labor_tipos_invalidos_lanza_type_error():
    area = AreaDeTrabajo("Cocina", [], [])
    with pytest.raises(TypeError):
        Labor("1", "Titulo", "Descripcion", 4, [], [], area)
    with pytest.raises(TypeError):
        Labor(1, "Titulo", "Descripcion", 4, [], [], "Cocina")
