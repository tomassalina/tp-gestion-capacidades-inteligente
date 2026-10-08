from franja import Franja


class AreaDeTrabajo:

    def __init__(self, nombre, credenciales_obligatorias, franjas):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")
        if not isinstance(credenciales_obligatorias, list):
            raise TypeError("credenciales_obligatorias debe ser una lista")
        if not isinstance(franjas, list) or not all(map(lambda f: isinstance(f, Franja), franjas)):
            raise TypeError("franjas debe ser una lista de Franja")

        self._nombre = nombre
        self._credenciales_obligatorias = credenciales_obligatorias
        self._franjas = franjas

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_credenciales_obligatorias(self):
        return self._credenciales_obligatorias

    def set_credenciales_obligatorias(self, credenciales_obligatorias):
        self._credenciales_obligatorias = credenciales_obligatorias

    def agregar_credencial_obligatoria(self, credencial):
        self._credenciales_obligatorias.append(credencial)

    def get_franjas(self):
        return self._franjas

    def set_franjas(self, franjas):
        self._franjas = franjas

    def buscar_franja(self, nombre_franja):
        return next(filter(lambda f: f.get_nombre() == nombre_franja, self._franjas), None)


def test_area_de_trabajo_tipos_invalidos_lanza_type_error():
    import pytest

    with pytest.raises(TypeError):
        AreaDeTrabajo(123, [], [])
    with pytest.raises(TypeError):
        AreaDeTrabajo("Cocina", "no es lista", [])
    with pytest.raises(TypeError):
        AreaDeTrabajo("Cocina", [], "no es lista")


def test_area_de_trabajo_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    import pytest

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
