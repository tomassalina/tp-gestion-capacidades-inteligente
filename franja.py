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
