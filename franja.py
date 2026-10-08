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
