class NivelHabilidad:

    BASICO = 1
    INTERMEDIO = 2
    AVANZADO = 3


class Habilidad:

    def __init__(self, nombre):
        self._nombre = nombre

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def __eq__(self, other):
        return isinstance(other, Habilidad) and self._nombre == other.get_nombre()

    def __hash__(self):
        return hash(self._nombre)


class HabilidadDeTrabajador:

    def __init__(self, habilidad, nivel):
        self._habilidad = habilidad
        self._nivel = nivel

    def get_habilidad(self):
        return self._habilidad

    def set_habilidad(self, habilidad):
        self._habilidad = habilidad

    def get_nivel(self):
        return self._nivel

    def set_nivel(self, nivel):
        self._nivel = nivel

    def cumple_nivel_minimo(self, nivel_minimo):
        return self._nivel >= nivel_minimo


class HabilidadRequerida:

    def __init__(self, habilidad, nivel_minimo):
        self._habilidad = habilidad
        self._nivel_minimo = nivel_minimo

    def get_habilidad(self):
        return self._habilidad

    def set_habilidad(self, habilidad):
        self._habilidad = habilidad

    def get_nivel_minimo(self):
        return self._nivel_minimo

    def set_nivel_minimo(self, nivel_minimo):
        self._nivel_minimo = nivel_minimo


def test_habilidad_igualdad_por_nombre():
    habilidad_a = Habilidad("Soldadura")
    habilidad_b = Habilidad("Soldadura")
    habilidad_c = Habilidad("Electricidad")
    assert habilidad_a == habilidad_b
    assert habilidad_a != habilidad_c
    assert hash(habilidad_a) == hash(habilidad_b)


def test_habilidad_de_trabajador_cumple_nivel_minimo():
    habilidad = Habilidad("Soldadura")
    propia = HabilidadDeTrabajador(habilidad, NivelHabilidad.INTERMEDIO)
    assert propia.cumple_nivel_minimo(NivelHabilidad.BASICO)
    assert propia.cumple_nivel_minimo(NivelHabilidad.INTERMEDIO)
    assert not propia.cumple_nivel_minimo(NivelHabilidad.AVANZADO)


def test_habilidad_requerida_getters():
    habilidad = Habilidad("Soldadura")
    requerida = HabilidadRequerida(habilidad, NivelHabilidad.AVANZADO)
    assert requerida.get_habilidad() == habilidad
    assert requerida.get_nivel_minimo() == NivelHabilidad.AVANZADO
