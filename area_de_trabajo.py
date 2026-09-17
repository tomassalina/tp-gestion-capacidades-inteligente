class AreaDeTrabajo:

    def __init__(self, nombre, credenciales_obligatorias, franjas):
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

    def get_franjas(self):
        return self._franjas

    def set_franjas(self, franjas):
        self._franjas = franjas

    def buscar_franja(self, nombre_franja):
        return next(filter(lambda franja: franja.get_nombre() == nombre_franja, self._franjas), None)
