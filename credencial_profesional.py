from datetime import date


class CredencialProfesional:

    def __init__(self, nombre, fecha_obtencion, fecha_caducidad):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")
        if not isinstance(fecha_obtencion, date):
            raise TypeError("fecha_obtencion debe ser un date")
        if not isinstance(fecha_caducidad, date):
            raise TypeError("fecha_caducidad debe ser un date")
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
