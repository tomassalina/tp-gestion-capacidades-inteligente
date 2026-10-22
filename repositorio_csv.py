import csv
import os


class RegistroNoEncontradoError(Exception):
    pass


class RegistroDuplicadoError(Exception):
    pass


def codificar_lista(items, a_texto):
    return ";".join(map(a_texto, items))


def decodificar_lista(texto, desde_texto):
    if texto == "":
        return []
    return list(map(desde_texto, texto.split(";")))


class RepositorioCSV:

    def __init__(self, ruta_archivo, columnas):
        if not isinstance(ruta_archivo, str):
            raise TypeError("ruta_archivo debe ser un string")
        if not isinstance(columnas, list) or not all(map(lambda c: isinstance(c, str), columnas)):
            raise TypeError("columnas debe ser una lista de strings")
        if "id" not in columnas:
            raise ValueError("columnas debe incluir 'id'")

        self._ruta_archivo = ruta_archivo
        self._columnas = columnas

        if not os.path.exists(self._ruta_archivo):
            self._escribir_filas([])

    def _leer_filas(self):
        with open(self._ruta_archivo, newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            return list(lector)

    def _escribir_filas(self, filas):
        with open(self._ruta_archivo, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self._columnas)
            escritor.writeheader()
            escritor.writerows(filas)

    def create(self, **datos):
        if "id" not in datos:
            raise ValueError("create necesita un 'id'")

        id_nuevo = str(datos["id"])
        filas = self._leer_filas()
        if any(fila["id"] == id_nuevo for fila in filas):
            raise RegistroDuplicadoError(f"Ya existe un registro con id '{id_nuevo}'")

        fila_nueva = {columna: str(datos.get(columna, "")) for columna in self._columnas}
        filas.append(fila_nueva)
        self._escribir_filas(filas)
        return fila_nueva

    def find(self, id):
        id_buscado = str(id)
        filas = self._leer_filas()
        return next(filter(lambda fila: fila["id"] == id_buscado, filas), None)

    def find_all(self):
        return self._leer_filas()

    def update(self, id, **datos):
        id_buscado = str(id)
        filas = self._leer_filas()

        fila_encontrada = next(filter(lambda fila: fila["id"] == id_buscado, filas), None)
        if fila_encontrada is None:
            raise RegistroNoEncontradoError(f"No existe un registro con id '{id_buscado}'")

        for clave, valor in datos.items():
            fila_encontrada[clave] = str(valor)

        self._escribir_filas(filas)
        return fila_encontrada

    def delete(self, id):
        id_buscado = str(id)
        filas = self._leer_filas()
        filas_restantes = list(filter(lambda fila: fila["id"] != id_buscado, filas))

        if len(filas_restantes) == len(filas):
            raise RegistroNoEncontradoError(f"No existe un registro con id '{id_buscado}'")

        self._escribir_filas(filas_restantes)
