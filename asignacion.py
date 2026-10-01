class EstadoAsignacion:

    SUGERIDA = "Sugerida"
    PENDIENTE = "Pendiente"
    APROBADA = "Aprobada"


class HorasMaximasExcedidasError(Exception):
    pass


class TrabajadorNoAptoError(Exception):
    pass


class FranjaSinLugarError(Exception):
    pass


class AsignacionDuplicadaError(Exception):
    pass


class Asignacion:

    def __init__(self, trabajador, labor, franja, fecha):
        self._trabajador = trabajador
        self._labor = labor
        self._franja = franja
        self._fecha = fecha
        self._estado = EstadoAsignacion.PENDIENTE

    def get_trabajador(self):
        return self._trabajador

    def get_labor(self):
        return self._labor

    def get_franja(self):
        return self._franja

    def get_fecha(self):
        return self._fecha

    def get_estado(self):
        return self._estado

    def set_estado(self, estado):
        self._estado = estado

    def reasignar(self, nuevo_trabajador):
        if self._estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se puede reasignar una asignacion ya Aprobada")
        self._trabajador = nuevo_trabajador

    @staticmethod
    def validar_apto(trabajador, labor, franja, fecha, asignaciones_existentes):
        if not trabajador.tiene_habilidades(labor.get_habilidades_requeridas()):
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no tiene todas las habilidades requeridas por la labor '{labor.get_titulo()}'"
            )

        if not trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha):
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no tiene las credenciales de la labor activas en la fecha {fecha}"
            )

        if not trabajador.tiene_credenciales_activas(labor.get_area().get_credenciales_obligatorias(), fecha):
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no tiene las credenciales obligatorias del area '{labor.get_area().get_nombre()}' activas"
            )

        if not trabajador.puede_tomar_horas(labor.get_duracion_horas()):
            raise HorasMaximasExcedidasError(
                f"{trabajador.get_nombre()} superaria sus horas maximas semanales ({trabajador.get_horas_maximas_semana()}hs)"
            )

        if not franja.tiene_lugar():
            raise FranjaSinLugarError(
                f"La franja '{franja.get_nombre()}' del area '{labor.get_area().get_nombre()}' no tiene lugar disponible"
            )

        existe_asignacion = any(
            asignacion.get_labor() == labor and asignacion.get_franja() == franja and asignacion.get_fecha() == fecha
            for asignacion in asignaciones_existentes
        )
        if existe_asignacion:
            raise AsignacionDuplicadaError(
                f"La labor '{labor.get_titulo()}' ya tiene una asignacion para la franja '{franja.get_nombre()}' del {fecha}"
            )

    @staticmethod
    def crear(trabajador, labor, franja, fecha, asignaciones_existentes, estado=None):
        Asignacion.validar_apto(trabajador, labor, franja, fecha, asignaciones_existentes)

        trabajador.sumar_horas(labor.get_duracion_horas())
        franja.ocupar_lugar()
        nueva_asignacion = Asignacion(trabajador, labor, franja, fecha)
        if estado is not None:
            nueva_asignacion.set_estado(estado)
        print(
            f"Labor '{labor.get_titulo()}' asignada a {trabajador.get_nombre()} "
            f"en la franja '{franja.get_nombre()}' (estado: {nueva_asignacion.get_estado()})"
        )
        return nueva_asignacion

    def aprobar(self):
        self.set_estado(EstadoAsignacion.APROBADA)


from datetime import date
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from franja import Franja
from labor import Labor
from trabajador import Trabajador
from area_de_trabajo import AreaDeTrabajo


def _armar_escenario():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=1)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    return trabajador, labor, franja


def test_crear_asignacion_exitosa_queda_pendiente():
    trabajador, labor, franja = _armar_escenario()
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    assert asignacion is not None
    assert asignacion.get_estado() == EstadoAsignacion.PENDIENTE
    assert trabajador.get_horas_asignadas() == 4


def test_validar_apto_falla_si_franja_no_tiene_lugar():
    import pytest

    trabajador, labor, franja = _armar_escenario()
    franja.ocupar_lugar()
    with pytest.raises(FranjaSinLugarError):
        Asignacion.validar_apto(trabajador, labor, franja, date(2026, 1, 1), [])


def test_crear_lanza_asignacion_duplicada_error():
    import pytest

    trabajador, labor, _ = _armar_escenario()
    franja_grande = Franja("Manana", capacidad=5)
    primera = Asignacion.crear(trabajador, labor, franja_grande, date(2026, 1, 1), [])
    with pytest.raises(AsignacionDuplicadaError):
        Asignacion.crear(trabajador, labor, franja_grande, date(2026, 1, 1), [primera])


def test_reasignar_pendiente_cambia_trabajador():
    trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.reasignar(otro_trabajador)
    assert asignacion.get_trabajador() == otro_trabajador


def test_reasignar_aprobada_lanza_value_error():
    import pytest

    trabajador, labor, franja = _armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.aprobar()
    with pytest.raises(ValueError):
        asignacion.reasignar(otro_trabajador)
