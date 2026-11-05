class TipoFranja:

    MANIANA = "Manana"
    TARDE = "Tarde"
    NOCHE = "Noche"


NOMBRES_FRANJA_VALIDOS = (TipoFranja.MANIANA, TipoFranja.TARDE, TipoFranja.NOCHE)


class Franja:

    def __init__(self, nombre, capacidad):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre not in NOMBRES_FRANJA_VALIDOS:
            raise ValueError("nombre debe ser Manana, Tarde o Noche")
        if not isinstance(capacidad, int):
            raise TypeError("capacidad debe ser un int")
        if capacidad <= 0:
            raise ValueError("capacidad debe ser mayor a 0")

        self.nombre = nombre
        self.capacidad = capacidad
        self.trabajadores_asignados = 0

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre

    def get_capacidad(self):
        return self.capacidad

    def set_capacidad(self, capacidad):
        self.capacidad = capacidad

    def get_trabajadores_asignados(self):
        return self.trabajadores_asignados

    def tiene_lugar(self):
        return self.trabajadores_asignados < self.capacidad

    def ocupar_lugar(self):
        self.trabajadores_asignados += 1

    def liberar_lugar(self):
        if self.trabajadores_asignados > 0:
            self.trabajadores_asignados -= 1

    def a_texto(self):
        # no se persiste la ocupacion: se reconstruye sola cuando se recargan las asignaciones
        return f"{self.nombre}:{self.capacidad}"

    @staticmethod
    def desde_texto(texto):
        nombre, capacidad = texto.split(":")
        return Franja(nombre, int(capacidad))
