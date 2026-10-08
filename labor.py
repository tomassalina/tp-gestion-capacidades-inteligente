from area_de_trabajo import AreaDeTrabajo
from habilidad import HabilidadRequerida


class Labor:

    def __init__(self, id, titulo, descripcion, duracion_horas, habilidades_requeridas, credenciales_requeridas, area):
        if not isinstance(id, int):
            raise TypeError("id debe ser un int")
        if not isinstance(titulo, str):
            raise TypeError("titulo debe ser un string")
        if titulo.strip() == "":
            raise ValueError("titulo no puede estar vacio")
        if not isinstance(descripcion, str):
            raise TypeError("descripcion debe ser un string")
        if descripcion.strip() == "":
            raise ValueError("descripcion no puede estar vacia")
        if not isinstance(duracion_horas, (int, float)):
            raise TypeError("duracion_horas debe ser un numero")
        if duracion_horas <= 0:
            raise ValueError("La duracion en horas debe ser mayor a 0")
        if not isinstance(habilidades_requeridas, list) or not all(map(lambda h: isinstance(h, HabilidadRequerida), habilidades_requeridas)):
            raise TypeError("habilidades_requeridas debe ser una lista de HabilidadRequerida")
        if not isinstance(credenciales_requeridas, list):
            raise TypeError("credenciales_requeridas debe ser una lista")
        if not isinstance(area, AreaDeTrabajo):
            raise TypeError("area debe ser una instancia de AreaDeTrabajo")

        self._id = id
        self._titulo = titulo
        self._descripcion = descripcion
        self._duracion_horas = duracion_horas
        self._habilidades_requeridas = habilidades_requeridas
        self._credenciales_requeridas = credenciales_requeridas
        self._area = area

    def get_id(self):
        return self._id

    def get_titulo(self):
        return self._titulo

    def set_titulo(self, titulo):
        self._titulo = titulo

    def get_descripcion(self):
        return self._descripcion

    def set_descripcion(self, descripcion):
        self._descripcion = descripcion

    def get_duracion_horas(self):
        return self._duracion_horas

    def set_duracion_horas(self, duracion_horas):
        self._duracion_horas = duracion_horas

    def get_habilidades_requeridas(self):
        return self._habilidades_requeridas

    def set_habilidades_requeridas(self, habilidades_requeridas):
        self._habilidades_requeridas = habilidades_requeridas

    def get_credenciales_requeridas(self):
        return self._credenciales_requeridas

    def set_credenciales_requeridas(self, credenciales_requeridas):
        self._credenciales_requeridas = credenciales_requeridas

    def get_area(self):
        return self._area

    def set_area(self, area):
        self._area = area


def test_labor_duracion_invalida_lanza_value_error():
    import pytest

    with pytest.raises(ValueError):
        Labor(1, "Titulo", "Descripcion", 0, [], [], None)


def test_labor_se_crea_correctamente():
    area = AreaDeTrabajo("Cocina", [], [])
    labor = Labor(1, "Preparar almuerzo", "Cocinar el menu", 4, [], ["Carnet"], area)
    assert labor.get_titulo() == "Preparar almuerzo"
    assert labor.get_duracion_horas() == 4
    assert labor.get_area() == area


def test_labor_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    import pytest

    area = AreaDeTrabajo("Cocina", [], [])
    with pytest.raises(TypeError):
        Labor(1, "Titulo", "Descripcion", 4, ["no es habilidad requerida"], [], area)


def test_labor_tipos_invalidos_lanza_type_error():
    import pytest

    area = AreaDeTrabajo("Cocina", [], [])
    with pytest.raises(TypeError):
        Labor("1", "Titulo", "Descripcion", 4, [], [], area)
    with pytest.raises(TypeError):
        Labor(1, "Titulo", "Descripcion", 4, [], [], "Cocina")
