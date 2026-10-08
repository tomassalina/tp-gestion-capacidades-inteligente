import pytest

from area_de_trabajo import AreaDeTrabajo
from franja import Franja


def test_area_de_trabajo_tipos_invalidos_lanza_type_error():
    with pytest.raises(TypeError):
        AreaDeTrabajo(123, [], [])
    with pytest.raises(TypeError):
        AreaDeTrabajo("Cocina", "no es lista", [])
    with pytest.raises(TypeError):
        AreaDeTrabajo("Cocina", [], "no es lista")


def test_area_de_trabajo_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    with pytest.raises(TypeError):
        AreaDeTrabajo("Cocina", [], ["no es franja"])


def test_buscar_franja_encuentra_por_nombre():
    franja_manana = Franja("Manana", capacidad=1)
    franja_tarde = Franja("Tarde", capacidad=2)
    area = AreaDeTrabajo("Cocina", [], [franja_manana, franja_tarde])
    assert area.buscar_franja("Tarde") == franja_tarde


def test_buscar_franja_devuelve_none_si_no_existe():
    area = AreaDeTrabajo("Cocina", [], [])
    assert area.buscar_franja("Noche") is None


def test_agregar_credencial_obligatoria():
    area = AreaDeTrabajo("Cocina", ["Carnet de Manipulacion de Alimentos"], [])
    area.agregar_credencial_obligatoria("Certificado de Higiene")
    assert "Certificado de Higiene" in area.get_credenciales_obligatorias()
    assert len(area.get_credenciales_obligatorias()) == 2
