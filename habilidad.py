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

    def guardar(self, repo):
        repo.create(id=self._nombre, nombre=self._nombre)

    @staticmethod
    def cargar_todas(repo):
        return list(map(lambda fila: Habilidad(fila["nombre"]), repo.find_all()))


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

    def a_texto(self):
        return f"{self._habilidad.get_nombre()}:{self._nivel}"

    @staticmethod
    def desde_texto(texto, habilidades_por_nombre):
        nombre, nivel = texto.split(":")
        return HabilidadDeTrabajador(habilidades_por_nombre[nombre], int(nivel))


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

    def a_texto(self):
        return f"{self._habilidad.get_nombre()}:{self._nivel_minimo}"

    @staticmethod
    def desde_texto(texto, habilidades_por_nombre):
        nombre, nivel_minimo = texto.split(":")
        return HabilidadRequerida(habilidades_por_nombre[nombre], int(nivel_minimo))
