from trabajador import Trabajador
from asignacion import EstadoAsignacion


class Supervisor(Trabajador):

    def aprobar_asignacion(self, asignacion):
        asignacion.aprobar()

    def ejecutar_acciones_del_sistema(self, sistema):
        sistema.ejecutar_acciones_semanales()

    def aprobar_asignaciones_pendientes(self, sistema):
        for asignacion in sistema.obtener_asignaciones():
            if asignacion.get_estado() == EstadoAsignacion.PENDIENTE:
                self.aprobar_asignacion(asignacion)

    def reasignar_asignacion(self, asignacion, nuevo_trabajador):
        asignacion.reasignar(nuevo_trabajador)

    def rechazar_asignacion(self, asignacion, sistema):
        asignacion.rechazar()
        sistema.obtener_asignaciones().remove(asignacion)

    def agregar_regla_area(self, area, credencial):
        area.agregar_credencial_obligatoria(credencial)


from datetime import date
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from franja import Franja
from labor import Labor
from area_de_trabajo import AreaDeTrabajo
from asignacion import Asignacion
from sistema import Sistema


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
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(asignacion)
    supervisor.aprobar_asignaciones_pendientes(sistema)
    assert asignacion.get_estado() == EstadoAsignacion.APROBADA


def test_reasignar_asignacion_delega_en_asignacion():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(3, "Beto", [HabilidadDeTrabajador(Habilidad("Coccion"), NivelHabilidad.BASICO)], [], 20)
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    supervisor.reasignar_asignacion(asignacion, otro_trabajador)
    assert asignacion.get_trabajador() == otro_trabajador


def test_reasignar_asignacion_a_no_apto_lanza_error():
    import pytest
    from asignacion import TrabajadorNoAptoError

    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(3, "Beto", [], [], 20)
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    with pytest.raises(TrabajadorNoAptoError):
        supervisor.reasignar_asignacion(asignacion, otro_trabajador)


def test_rechazar_asignacion_la_saca_del_sistema():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(asignacion)
    supervisor.rechazar_asignacion(asignacion, sistema)
    assert asignacion not in sistema.obtener_asignaciones()
    assert trabajador.get_horas_asignadas() == 0


def test_agregar_regla_area_delega_en_area():
    supervisor, sistema, trabajador, labor, franja = _armar_escenario()
    area = labor.get_area()
    supervisor.agregar_regla_area(area, "Certificado de Higiene")
    assert "Certificado de Higiene" in area.get_credenciales_obligatorias()
