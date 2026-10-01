class Franja:

    def __init__(self, nombre, capacidad):
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


def test_franja_tiene_lugar_inicialmente():
    franja = Franja("Manana", capacidad=2)
    assert franja.tiene_lugar()


def test_franja_se_completa_al_ocupar_todo_el_lugar():
    franja = Franja("Manana", capacidad=1)
    franja.ocupar_lugar()
    assert not franja.tiene_lugar()
    assert franja.get_trabajadores_asignados() == 1
