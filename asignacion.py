from datetime import date
from franja import Franja
from labor import Labor
from trabajador import Trabajador


class EstadoAsignacion:

    AUTOMATICA = "Automatica"
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

    def __init__(self, trabajador, labor, franja, fecha, asignaciones_existentes, estado=None):
        if not isinstance(trabajador, Trabajador):
            raise TypeError("trabajador debe ser una instancia de Trabajador")
        if not isinstance(labor, Labor):
            raise TypeError("labor debe ser una instancia de Labor")
        if not isinstance(franja, Franja):
            raise TypeError("franja debe ser una instancia de Franja")
        if not isinstance(fecha, date):
            raise TypeError("fecha debe ser un date")
        if estado is not None and estado not in (EstadoAsignacion.AUTOMATICA, EstadoAsignacion.PENDIENTE, EstadoAsignacion.APROBADA):
            raise ValueError("estado debe ser uno de los valores definidos en EstadoAsignacion")

        Asignacion.validar_apto(trabajador, labor, franja, fecha, asignaciones_existentes)

        trabajador.sumar_horas(labor.get_duracion_horas())
        franja.ocupar_lugar()

        self._trabajador = trabajador
        self._labor = labor
        self._franja = franja
        self._fecha = fecha
        self._estado = estado if estado is not None else EstadoAsignacion.PENDIENTE
        print(
            f"Labor '{labor.get_titulo()}' asignada a {trabajador.get_nombre()} "
            f"en la franja '{franja.get_nombre()}' (estado: {self._estado})"
        )

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

        if not nuevo_trabajador.tiene_habilidades(self._labor.get_habilidades_requeridas()):
            raise TrabajadorNoAptoError(
                f"{nuevo_trabajador.get_nombre()} no tiene todas las habilidades requeridas por la labor '{self._labor.get_titulo()}'"
            )
        if not nuevo_trabajador.tiene_credenciales_activas(self._labor.get_credenciales_requeridas(), self._fecha):
            raise TrabajadorNoAptoError(
                f"{nuevo_trabajador.get_nombre()} no tiene las credenciales de la labor activas en la fecha {self._fecha}"
            )
        if not nuevo_trabajador.tiene_credenciales_activas(self._labor.get_area().get_credenciales_obligatorias(), self._fecha):
            raise TrabajadorNoAptoError(
                f"{nuevo_trabajador.get_nombre()} no tiene las credenciales obligatorias del area '{self._labor.get_area().get_nombre()}' activas"
            )
        if not nuevo_trabajador.puede_tomar_horas(self._labor.get_duracion_horas()):
            raise HorasMaximasExcedidasError(
                f"{nuevo_trabajador.get_nombre()} superaria sus horas maximas semanales ({nuevo_trabajador.get_horas_maximas_semana()}hs)"
            )

        self._trabajador.restar_horas(self._labor.get_duracion_horas())
        nuevo_trabajador.sumar_horas(self._labor.get_duracion_horas())
        self._trabajador = nuevo_trabajador

    def rechazar(self):
        if self._estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se puede rechazar una asignacion ya Aprobada")
        self._trabajador.restar_horas(self._labor.get_duracion_horas())
        self._franja.liberar_lugar()

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

    def aprobar(self):
        self.set_estado(EstadoAsignacion.APROBADA)
