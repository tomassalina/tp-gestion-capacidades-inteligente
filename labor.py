from area_de_trabajo import AreaDeTrabajo
from habilidad import HabilidadRequerida
from repositorio_csv import codificar_lista, decodificar_lista


class Labor:

    def __init__(self, id, titulo, descripcion, duracion_horas, habilidades_requeridas, credenciales_requeridas, area):
        if not isinstance(id, int):
            raise TypeError("id debe ser un int")
        if not isinstance(titulo, str):
            raise TypeError("titulo debe ser un string")
        if titulo.strip() == "":
            raise ValueError("titulo no puede estar vacio")
        if not isinstance(descripcion, str):
            raise TypeError("descripcion debe ser un string")
        if descripcion.strip() == "":
            raise ValueError("descripcion no puede estar vacia")
        if not isinstance(duracion_horas, (int, float)):
            raise TypeError("duracion_horas debe ser un numero")
        if duracion_horas <= 0:
            raise ValueError("La duracion en horas debe ser mayor a 0")
        if not isinstance(habilidades_requeridas, list) or not all(map(lambda h: isinstance(h, HabilidadRequerida), habilidades_requeridas)):
            raise TypeError("habilidades_requeridas debe ser una lista de HabilidadRequerida")
        if not isinstance(credenciales_requeridas, list):
            raise TypeError("credenciales_requeridas debe ser una lista")
        if not isinstance(area, AreaDeTrabajo):
            raise TypeError("area debe ser una instancia de AreaDeTrabajo")

        self._id = id
        self._titulo = titulo
        self._descripcion = descripcion
        self._duracion_horas = duracion_horas
        self._habilidades_requeridas = habilidades_requeridas
        self._credenciales_requeridas = credenciales_requeridas
        self._area = area

    def get_id(self):
        return self._id

    def get_titulo(self):
        return self._titulo

    def set_titulo(self, titulo):
        self._titulo = titulo

    def get_descripcion(self):
        return self._descripcion

    def set_descripcion(self, descripcion):
        self._descripcion = descripcion

    def get_duracion_horas(self):
        return self._duracion_horas

    def set_duracion_horas(self, duracion_horas):
        self._duracion_horas = duracion_horas

    def get_habilidades_requeridas(self):
        return self._habilidades_requeridas

    def set_habilidades_requeridas(self, habilidades_requeridas):
        self._habilidades_requeridas = habilidades_requeridas

    def get_credenciales_requeridas(self):
        return self._credenciales_requeridas

    def set_credenciales_requeridas(self, credenciales_requeridas):
        self._credenciales_requeridas = credenciales_requeridas

    def get_area(self):
        return self._area

    def set_area(self, area):
        self._area = area

    def guardar(self, repo):
        repo.create(
            id=self._id,
            titulo=self._titulo,
            descripcion=self._descripcion,
            duracion_horas=self._duracion_horas,
            habilidades_requeridas=codificar_lista(self._habilidades_requeridas, lambda h: h.a_texto()),
            credenciales_requeridas=codificar_lista(self._credenciales_requeridas, lambda c: c),
            area=self._area.get_nombre(),
        )

    @staticmethod
    def cargar_todas(repo, areas_por_nombre, habilidades_por_nombre):
        labores = []
        for fila in repo.find_all():
            habilidades_requeridas = decodificar_lista(
                fila["habilidades_requeridas"],
                lambda texto: HabilidadRequerida.desde_texto(texto, habilidades_por_nombre),
            )
            credenciales_requeridas = decodificar_lista(fila["credenciales_requeridas"], lambda c: c)
            labores.append(Labor(
                int(fila["id"]),
                fila["titulo"],
                fila["descripcion"],
                float(fila["duracion_horas"]),
                habilidades_requeridas,
                credenciales_requeridas,
                areas_por_nombre[fila["area"]],
            ))
        return labores
