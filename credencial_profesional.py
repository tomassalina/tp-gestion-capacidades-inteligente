from datetime import date


class CredencialProfesional:

    def __init__(self, nombre, fecha_obtencion, fecha_caducidad):
        if fecha_caducidad <= fecha_obtencion:
            raise ValueError("La fecha de caducidad debe ser posterior a la fecha de obtencion")

        self.nombre = nombre
        self.fecha_obtencion = fecha_obtencion
        self.fecha_caducidad = fecha_caducidad

    def esta_activa(self, fecha_referencia):
        return self.fecha_obtencion <= fecha_referencia <= self.fecha_caducidad
