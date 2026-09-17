class CredencialProfesional:

    def __init__(self, nombre, fecha_obtencion, fecha_caducidad):
        if fecha_caducidad <= fecha_obtencion:
            raise ValueError("La fecha de caducidad debe ser posterior a la fecha de obtencion")

        self._nombre = nombre
        self._fecha_obtencion = fecha_obtencion
        self._fecha_caducidad = fecha_caducidad

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_fecha_obtencion(self):
        return self._fecha_obtencion

    def set_fecha_obtencion(self, fecha_obtencion):
        self._fecha_obtencion = fecha_obtencion

    def get_fecha_caducidad(self):
        return self._fecha_caducidad

    def set_fecha_caducidad(self, fecha_caducidad):
        self._fecha_caducidad = fecha_caducidad

    def esta_activa(self, fecha_referencia):
        return self._fecha_obtencion <= fecha_referencia <= self._fecha_caducidad
