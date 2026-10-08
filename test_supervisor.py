from datetime import date
from unittest.mock import MagicMock

import pytest

from area_de_trabajo import AreaDeTrabajo
from asignacion import Asignacion, EstadoAsignacion, TrabajadorNoAptoError
from franja import Franja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador


def _armar_escenario():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=1)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    supervisor = Supervisor(2, "Carla", [], [], 20)
    sistema = Sistema(trabajadores=[trabajador], areas=[area], labores=[labor])
    return supervisor, sistema, trabajador, labor, franja


def test_aprobar_asignaciones_pendientes_cambia_estado():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(asignacion)
    supervisor.aprobar_asignaciones_pendientes(sistema)
    assert asignacion.get_estado() == EstadoAsignacion.APROBADA


def test_reasignar_asignacion_delega_en_asignacion():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(3, "Beto", [HabilidadDeTrabajador(Habilidad("Coccion"), NivelHabilidad.BASICO)], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    supervisor.reasignar_asignacion(asignacion, otro_trabajador)
    assert asignacion.get_trabajador() == otro_trabajador


def test_reasignar_asignacion_a_no_apto_lanza_error():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(3, "Beto", [], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    with pytest.raises(TrabajadorNoAptoError):
        supervisor.reasignar_asignacion(asignacion, otro_trabajador)


def test_rechazar_asignacion_la_saca_del_sistema():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(asignacion)
    supervisor.rechazar_asignacion(asignacion, sistema)
    assert asignacion not in sistema.obtener_asignaciones()
    assert trabajador.get_horas_asignadas() == 0


def test_agregar_regla_area_delega_en_area():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    area = labor.get_area()
    supervisor.agregar_regla_area(area, "Certificado de Higiene")
    assert "Certificado de Higiene" in area.get_credenciales_obligatorias()


def test_asignar_trabajador_crea_asignacion_aprobada():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    fecha = date(2026, 1, 1)
    nueva = supervisor.asignar_trabajador(sistema, trabajador, labor, franja, fecha)
    assert nueva.get_estado() == EstadoAsignacion.APROBADA
    assert nueva in sistema.obtener_asignaciones()
    assert trabajador.get_horas_asignadas() == labor.get_duracion_horas()


def test_asignar_trabajador_no_apto_lanza_error():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(3, "Beto", [], [], 20)
    with pytest.raises(TrabajadorNoAptoError):
        supervisor.asignar_trabajador(sistema, otro_trabajador, labor, franja, date(2026, 1, 1))
    assert sistema.obtener_asignaciones() == []


def test_asignar_trabajador_delega_en_sistema_con_mock():
    supervisor = Supervisor(2, "Carla", [], [], 20)
    trabajador = Trabajador(1, "Ana", [], [], 20)
    labor_mock = MagicMock()
    franja_mock = MagicMock()
    sistema_mock = MagicMock()
    sistema_mock.obtener_asignaciones.return_value = []

    with pytest.raises(TypeError):
        supervisor.asignar_trabajador(sistema_mock, trabajador, labor_mock, franja_mock, date(2026, 1, 1))
    sistema_mock.obtener_asignaciones.assert_called()
