class NivelHabilidad:
    """Constantes de nivel. Son numeros simples para poder compararlos con >=."""

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
    """Une una Habilidad con el nivel que un Trabajador tiene de ella."""

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
    """Une una Habilidad con el nivel minimo que exige una Labor."""

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
