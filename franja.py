class TipoFranja:

    MANIANA = "Manana"
    TARDE = "Tarde"
    NOCHE = "Noche"


class Franja:

    def __init__(self, nombre, capacidad):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre not in (TipoFranja.MANIANA, TipoFranja.TARDE, TipoFranja.NOCHE):
            raise ValueError("nombre debe ser Manana, Tarde o Noche")
        if not isinstance(capacidad, int):
            raise TypeError("capacidad debe ser un int")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser mayor a 0")

        self._nombre = nombre
        self._capacidad = capacidad
        self._trabajadores_asignados = 0

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_capacidad(self):
        return self._capacidad

    def set_capacidad(self, capacidad):
        self._capacidad = capacidad

    def get_trabajadores_asignados(self):
        return self._trabajadores_asignados

    def tiene_lugar(self):
        return self._trabajadores_asignados < self._capacidad

    def ocupar_lugar(self):
        self._trabajadores_asignados += 1

    def liberar_lugar(self):
        if self._trabajadores_asignados > 0:
            self._trabajadores_asignados -= 1


def test_franja_tiene_lugar_inicialmente():
    franja = Franja(TipoFranja.MANIANA, capacidad=2)
    assert franja.tiene_lugar()


def test_franja_nombre_fuera_del_tipo_lanza_value_error():
    import pytest

    with pytest.raises(ValueError):
        Franja("Madrugada", capacidad=2)


def test_franja_tipos_o_valores_invalidos_lanza_error():
    import pytest

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
