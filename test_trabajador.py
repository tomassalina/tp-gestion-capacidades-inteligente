from datetime import date
from unittest.mock import MagicMock

import pytest

from credencial_profesional import CredencialProfesional
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from trabajador import Trabajador


def test_horas_maximas_invalidas_lanza_value_error():
    with pytest.raises(ValueError):
        Trabajador(1, "Ana", [], [], 0)


def test_trabajador_tipos_invalidos_lanza_type_error():
    with pytest.raises(TypeError):
        Trabajador("1", "Ana", [], [], 20)
    with pytest.raises(TypeError):
        Trabajador(1, "Ana", "no es lista", [], 20)


def test_trabajador_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    with pytest.raises(TypeError):
        Trabajador(1, "Ana", ["no es habilidad"], [], 20)
    with pytest.raises(TypeError):
        Trabajador(1, "Ana", [], ["no es credencial"], 20)


def test_tiene_habilidades_respeta_nivel_minimo():
    soldadura = Habilidad("Soldadura")
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(soldadura, NivelHabilidad.BASICO)], [], 20)
    requerida_baja = [HabilidadRequerida(soldadura, NivelHabilidad.BASICO)]
    requerida_alta = [HabilidadRequerida(soldadura, NivelHabilidad.AVANZADO)]
    assert trabajador.tiene_habilidades(requerida_baja)
    assert not trabajador.tiene_habilidades(requerida_alta)


def test_puede_tomar_horas_respeta_limite_semanal():
    trabajador = Trabajador(1, "Ana", [], [], 10)
    trabajador.sumar_horas(8)
    assert not trabajador.puede_tomar_horas(4)
    assert trabajador.puede_tomar_horas(2)


def test_restar_horas_nunca_queda_negativo():
    trabajador = Trabajador(1, "Ana", [], [], 10)
    trabajador.sumar_horas(4)
    trabajador.restar_horas(4)
    assert trabajador.get_horas_asignadas() == 0
    trabajador.restar_horas(4)
    assert trabajador.get_horas_asignadas() == 0


def test_atributos_opcionales_por_kwargs():
    trabajador = Trabajador(1, "Diego", [], [], 15, idioma="Ingles")
    assert trabajador.get_atributo("idioma") == "Ingles"
    assert trabajador.get_atributo("inexistente", "default") == "default"


def test_tiene_credenciales_activas_respeta_todas_las_requeridas():
    vigente = CredencialProfesional("Carnet", date(2025, 1, 1), date(2027, 1, 1))
    trabajador = Trabajador(1, "Ana", [], [vigente], 20)
    assert trabajador.tiene_credenciales_activas(["Carnet"], date(2026, 1, 1))
    assert not trabajador.tiene_credenciales_activas(["Carnet", "Otra"], date(2026, 1, 1))


def test_solicitar_asignacion_delega_en_el_sistema_con_mock():
    trabajador = Trabajador(1, "Ana", [], [], 20)
    labor_mock = MagicMock()
    franja_mock = MagicMock()
    fecha = date(2026, 1, 1)
    sistema_mock = MagicMock()

    trabajador.solicitar_asignacion(sistema_mock, labor_mock, franja_mock, fecha)

    sistema_mock.solicitar_asignacion.assert_called_once_with(trabajador, labor_mock, franja_mock, fecha)
