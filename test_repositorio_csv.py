import os

import pytest

from repositorio_csv import RegistroDuplicadoError, RegistroNoEncontradoError, RepositorioCSV, codificar_lista, decodificar_lista


@pytest.fixture
def repo(tmp_path):
    ruta = os.path.join(tmp_path, "cosas.csv")
    return RepositorioCSV(ruta, ["id", "nombre", "valor"])


def test_repositorio_arranca_vacio(repo):
    assert repo.find_all() == []
    assert repo.find(1) is None


def test_create_agrega_una_fila(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    filas = repo.find_all()
    assert len(filas) == 1
    assert filas[0]["id"] == "1"
    assert filas[0]["nombre"] == "Ana"


def test_create_sin_id_lanza_value_error(repo):
    with pytest.raises(ValueError):
        repo.create(nombre="Ana")


def test_create_duplicado_lanza_error(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    with pytest.raises(RegistroDuplicadoError):
        repo.create(id=1, nombre="Otra", valor="20")


def test_find_devuelve_la_fila_correcta(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    repo.create(id=2, nombre="Beto", valor="20")
    encontrada = repo.find(2)
    assert encontrada["nombre"] == "Beto"


def test_find_con_id_inexistente_devuelve_none(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    assert repo.find(999) is None


def test_update_modifica_solo_los_campos_pasados(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    repo.update(1, valor="99")
    fila = repo.find(1)
    assert fila["nombre"] == "Ana"
    assert fila["valor"] == "99"


def test_update_id_inexistente_lanza_error(repo):
    with pytest.raises(RegistroNoEncontradoError):
        repo.update(999, valor="99")


def test_delete_saca_la_fila(repo):
    repo.create(id=1, nombre="Ana", valor="10")
    repo.create(id=2, nombre="Beto", valor="20")
    repo.delete(1)
    assert repo.find_all() == [{"id": "2", "nombre": "Beto", "valor": "20"}]


def test_delete_id_inexistente_lanza_error(repo):
    with pytest.raises(RegistroNoEncontradoError):
        repo.delete(999)


def test_los_datos_sobreviven_a_una_nueva_instancia_del_repositorio(tmp_path):
    ruta = os.path.join(tmp_path, "persistencia.csv")
    RepositorioCSV(ruta, ["id", "nombre", "valor"]).create(id=1, nombre="Ana", valor="10")

    repo_reabierto = RepositorioCSV(ruta, ["id", "nombre", "valor"])
    assert repo_reabierto.find(1)["nombre"] == "Ana"


@pytest.mark.parametrize(
    "columnas, excepcion_esperada",
    [
        pytest.param("no es lista", TypeError, id="columnas_no_es_lista"),
        pytest.param([1, 2], TypeError, id="columnas_con_elemento_no_string"),
        pytest.param(["nombre", "valor"], ValueError, id="columnas_sin_id"),
    ],
)
def test_repositorio_valida_columnas_al_construirse(tmp_path, columnas, excepcion_esperada):
    ruta = os.path.join(tmp_path, "invalido.csv")
    with pytest.raises(excepcion_esperada):
        RepositorioCSV(ruta, columnas)


def test_codificar_y_decodificar_lista_son_inversas():
    numeros = [1, 2, 3]
    texto = codificar_lista(numeros, str)
    assert texto == "1;2;3"
    assert decodificar_lista(texto, int) == numeros


def test_decodificar_lista_vacia_devuelve_lista_vacia():
    assert decodificar_lista("", int) == []
