from area_de_trabajo import AreaDeTrabajo


class Labor:

    def __init__(self, id, titulo, descripcion, duracion_horas, habilidades_requeridas, credenciales_requeridas, area):
        if duracion_horas <= 0:
            raise ValueError("La duracion en horas debe ser mayor a 0")

        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.duracion_horas = duracion_horas
        self.habilidades_requeridas = habilidades_requeridas
        self.credenciales_requeridas = credenciales_requeridas
        self.area = area
