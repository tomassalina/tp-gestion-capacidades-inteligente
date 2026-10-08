class NivelHabilidad:

    BASICO = 1
    INTERMEDIO = 2
    AVANZADO = 3


NIVELES_HABILIDAD = (NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO)


class Habilidad:

    def __init__(self, nombre):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")

        self._nombre = nombre

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def __eq__(self, other):
        return isinstance(other, Habilidad) and self._nombre == other.get_nombre()


class HabilidadDeTrabajador:

    def __init__(self, habilidad, nivel):
        if not isinstance(habilidad, Habilidad):
            raise TypeError("habilidad debe ser una instancia de Habilidad")
        if nivel not in NIVELES_HABILIDAD:
            raise ValueError("nivel debe ser uno de los valores definidos en NivelHabilidad")

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
        if not isinstance(habilidad, Habilidad):
            raise TypeError("habilidad debe ser una instancia de Habilidad")
        if nivel_minimo not in NIVELES_HABILIDAD:
            raise ValueError("nivel_minimo debe ser uno de los valores definidos en NivelHabilidad")

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


def test_habilidad_tipo_o_valor_invalido_lanza_error():
    import pytest

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
    import pytest

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
    import pytest

    habilidad = Habilidad("Soldadura")
    with pytest.raises(TypeError):
        HabilidadRequerida("no es habilidad", NivelHabilidad.BASICO)
    with pytest.raises(ValueError):
        HabilidadRequerida(habilidad, 99)
