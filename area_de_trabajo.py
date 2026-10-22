from franja import Franja
from repositorio_csv import codificar_lista, decodificar_lista


class AreaDeTrabajo:

    def __init__(self, nombre, credenciales_obligatorias, franjas):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")
        if not isinstance(credenciales_obligatorias, list):
            raise TypeError("credenciales_obligatorias debe ser una lista")
        if not isinstance(franjas, list) or not all(map(lambda f: isinstance(f, Franja), franjas)):
            raise TypeError("franjas debe ser una lista de Franja")

        self._nombre = nombre
        self._credenciales_obligatorias = credenciales_obligatorias
        self._franjas = franjas
        self._franjas_por_nombre = {franja.get_nombre(): franja for franja in franjas}

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_credenciales_obligatorias(self):
        return self._credenciales_obligatorias

    def set_credenciales_obligatorias(self, credenciales_obligatorias):
        self._credenciales_obligatorias = credenciales_obligatorias

    def agregar_credencial_obligatoria(self, credencial):
        self._credenciales_obligatorias.append(credencial)

    def get_franjas(self):
        return self._franjas

    def set_franjas(self, franjas):
        self._franjas = franjas
        self._franjas_por_nombre = {franja.get_nombre(): franja for franja in franjas}

    def buscar_franja(self, nombre_franja):
        return self._franjas_por_nombre.get(nombre_franja)

    def guardar(self, repo):
        repo.create(
            id=self._nombre,
            nombre=self._nombre,
            credenciales_obligatorias=codificar_lista(self._credenciales_obligatorias, lambda c: c),
            franjas=codificar_lista(self._franjas, lambda f: f.a_texto()),
        )

    @staticmethod
    def cargar_todas(repo):
        areas = []
        for fila in repo.find_all():
            credenciales = decodificar_lista(fila["credenciales_obligatorias"], lambda c: c)
            franjas = decodificar_lista(fila["franjas"], Franja.desde_texto)
            areas.append(AreaDeTrabajo(fila["nombre"], credenciales, franjas))
        return areas
