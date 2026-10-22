import os
from datetime import date

import pytest

from area_de_trabajo import AreaDeTrabajo
from credencial_profesional import CredencialProfesional
from franja import Franja, TipoFranja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from repositorio_csv import RepositorioCSV
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador


def test_habilidad_guarda_y_se_recarga(tmp_path):
    repo = RepositorioCSV(os.path.join(tmp_path, "habilidades.csv"), ["id", "nombre"])
    Habilidad("Python").guardar(repo)
    Habilidad("SQL").guardar(repo)

    recargadas = Habilidad.cargar_todas(repo)

    assert sorted(map(lambda h: h.get_nombre(), recargadas)) == ["Python", "SQL"]


def test_trabajador_con_atributos_opcionales_guarda_y_se_recarga(tmp_path):
    repo = RepositorioCSV(
        os.path.join(tmp_path, "trabajadores.csv"),
        ["id", "nombre", "habilidades", "credenciales", "horas_maximas_semana", "atributos"],
    )
    python = Habilidad("Python")
    credencial = CredencialProfesional("NDA Firmado", date(2025, 1, 1), date(2027, 1, 1))
    original = Trabajador(
        1, "Ana", [HabilidadDeTrabajador(python, NivelHabilidad.AVANZADO)], [credencial], 20,
        rol="Dev", area_equipo="Backend",
    )

    original.guardar(repo)
    recargado = Trabajador.cargar_todos(repo, {"Python": python})[0]

    assert recargado.get_id() == 1
    assert recargado.get_nombre() == "Ana"
    assert recargado.get_habilidades()[0].get_nivel() == NivelHabilidad.AVANZADO
    assert recargado.get_credenciales()[0].get_nombre() == "NDA Firmado"
    assert recargado.get_atributo("rol") == "Dev"
    assert recargado.get_atributo("area_equipo") == "Backend"
    assert isinstance(recargado, Trabajador)
    assert not isinstance(recargado, Supervisor)


@pytest.fixture
def escenario_completo():
    habilidad = Habilidad("Python")
    franja_manana = Franja(TipoFranja.MANIANA, capacidad=2)
    franja_tarde = Franja(TipoFranja.TARDE, capacidad=1)
    area = AreaDeTrabajo("Backend", ["NDA Firmado"], [franja_manana, franja_tarde])
    labor = Labor(
        1, "Armar API", "Un endpoint nuevo", 4,
        [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], ["NDA Firmado"], area,
    )
    credencial = CredencialProfesional("NDA Firmado", date(2025, 1, 1), date(2027, 1, 1))
    ana = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.INTERMEDIO)], [credencial], 20)
    beto = Trabajador(2, "Beto", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [credencial], 20)
    carla = Supervisor(3, "Carla", [], [], 20, rol="Manager")

    sistema = Sistema(trabajadores=[ana, beto, carla], areas=[area], labores=[labor])
    sistema.solicitar_asignacion(ana, labor, franja_manana, date(2026, 1, 1))
    carla.asignar_trabajador(sistema, beto, labor, franja_tarde, date(2026, 1, 2))
    return sistema


def test_sistema_guarda_y_recarga_todo_el_grafo(tmp_path, escenario_completo):
    directorio = os.path.join(tmp_path, "datos")
    escenario_completo.guardar_todo(directorio)

    recargado = Sistema.cargar_todo(directorio)

    assert len(recargado.get_trabajadores()) == 3
    assert isinstance(recargado.buscar_trabajador_por_id(3), Supervisor)
    assert not isinstance(recargado.buscar_trabajador_por_id(1), Supervisor)

    ana_recargada = recargado.buscar_trabajador_por_id(1)
    assert ana_recargada.get_habilidades()[0].get_nivel() == NivelHabilidad.INTERMEDIO

    asignaciones = recargado.obtener_asignaciones()
    assert len(asignaciones) == 1
    assert asignaciones[0].get_trabajador().get_nombre() == "Beto"
    assert asignaciones[0].get_estado() == "Aprobada"

    assert len(recargado.get_solicitudes_pendientes()) == 1


def test_sistema_recargado_comparte_la_misma_habilidad_entre_trabajador_y_labor(tmp_path, escenario_completo):
    directorio = os.path.join(tmp_path, "datos")
    escenario_completo.guardar_todo(directorio)

    recargado = Sistema.cargar_todo(directorio)

    habilidad_de_ana = recargado.buscar_trabajador_por_id(1).get_habilidades()[0].get_habilidad()
    habilidad_de_la_labor = recargado.get_labores()[0].get_habilidades_requeridas()[0].get_habilidad()
    assert habilidad_de_ana is habilidad_de_la_labor
