from datetime import date

import pytest

from area_de_trabajo import AreaDeTrabajo
from asignacion import (
    Asignacion,
    AsignacionDuplicadaError,
    EstadoAsignacion,
    FranjaSinLugarError,
    HorasMaximasExcedidasError,
    TrabajadorNoAptoError,
)
from franja import Franja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from trabajador import Trabajador


def _armar_escenario():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=1)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    return trabajador, labor, franja


def test_asignacion_tipo_o_estado_invalido_lanza_error():
    trabajador, labor, franja = _armar_escenario()
    with pytest.raises(TypeError):
        Asignacion("no es trabajador", labor, franja, date(2026, 1, 1), [])
    with pytest.raises(ValueError):
        Asignacion(trabajador, labor, franja, date(2026, 1, 1), [], estado="Invalido")


def test_crear_asignacion_exitosa_queda_pendiente():
    trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    assert asignacion is not None
    assert asignacion.get_estado() == EstadoAsignacion.PENDIENTE
    assert trabajador.get_horas_asignadas() == 4


def test_validar_apto_falla_si_franja_no_tiene_lugar():
    trabajador, labor, franja = _armar_escenario()
    franja.ocupar_lugar()
    with pytest.raises(FranjaSinLugarError):
        Asignacion.validar_apto(trabajador, labor, franja, date(2026, 1, 1), [])


def test_crear_lanza_asignacion_duplicada_error():
    trabajador, labor, _ = _armar_escenario()
    franja_grande = Franja("Manana", capacidad=5)
    primera = Asignacion(trabajador, labor, franja_grande, date(2026, 1, 1), [])
    with pytest.raises(AsignacionDuplicadaError):
        Asignacion(trabajador, labor, franja_grande, date(2026, 1, 1), [primera])


def test_reasignar_pendiente_cambia_trabajador():
    trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [HabilidadDeTrabajador(Habilidad("Coccion"), NivelHabilidad.BASICO)], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.reasignar(otro_trabajador)
    assert asignacion.get_trabajador() == otro_trabajador
    assert trabajador.get_horas_asignadas() == 0
    assert otro_trabajador.get_horas_asignadas() == 4


def test_reasignar_a_trabajador_no_apto_lanza_error():
    trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    with pytest.raises(TrabajadorNoAptoError):
        asignacion.reasignar(otro_trabajador)
    assert asignacion.get_trabajador() == trabajador


def test_rechazar_libera_horas_y_franja():
    trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.rechazar()
    assert trabajador.get_horas_asignadas() == 0
    assert franja.tiene_lugar()


def test_rechazar_aprobada_lanza_value_error():
    trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.aprobar()
    with pytest.raises(ValueError):
        asignacion.rechazar()


def test_reasignar_aprobada_lanza_value_error():
    trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.aprobar()
    with pytest.raises(ValueError):
        asignacion.reasignar(otro_trabajador)


def test_validar_apto_con_mock_de_trabajador_no_habilitado():
    from unittest.mock import MagicMock

    _, labor, franja = _armar_escenario()
    trabajador_mock = MagicMock()
    trabajador_mock.get_nombre.return_value = "Mockeado"
    trabajador_mock.tiene_habilidades.return_value = False
    with pytest.raises(TrabajadorNoAptoError):
        Asignacion.validar_apto(trabajador_mock, labor, franja, date(2026, 1, 1), [])
