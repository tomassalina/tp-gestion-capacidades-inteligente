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

    def __init__(self, mensaje, habilidades_faltantes=None, credenciales_faltantes=None):
        super().__init__(mensaje)
        self.habilidades_faltantes = habilidades_faltantes if habilidades_faltantes is not None else set()
        self.credenciales_faltantes = credenciales_faltantes if credenciales_faltantes is not None else set()


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

        self.trabajador = trabajador
        self.labor = labor
        self.franja = franja
        self.fecha = fecha
        self.estado = estado if estado is not None else EstadoAsignacion.PENDIENTE
        trabajador.agregar_a_agenda(self)
        print(
            f"Labor '{labor.get_titulo()}' asignada a {trabajador.get_nombre()} "
            f"en la franja '{franja.get_nombre()}' (estado: {self.estado})"
        )

    def get_trabajador(self):
        return self.trabajador

    def get_labor(self):
        return self.labor

    def get_franja(self):
        return self.franja

    def get_fecha(self):
        return self.fecha

    def get_estado(self):
        return self.estado

    def set_estado(self, estado):
        self.estado = estado

    def reasignar(self, nuevo_trabajador):
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se puede reasignar una asignacion ya Aprobada")

        Asignacion.evaluar_aptitud(nuevo_trabajador, self.labor, self.fecha)

        self.trabajador.restar_horas(self.labor.get_duracion_horas())
        self.trabajador.sacar_de_agenda(self)
        nuevo_trabajador.sumar_horas(self.labor.get_duracion_horas())
        nuevo_trabajador.agregar_a_agenda(self)
        self.trabajador = nuevo_trabajador

    def rechazar(self):
        if self.estado == EstadoAsignacion.APROBADA:
            raise ValueError("No se puede rechazar una asignacion ya Aprobada")
        self.trabajador.restar_horas(self.labor.get_duracion_horas())
        self.trabajador.sacar_de_agenda(self)

    @staticmethod
    def evaluar_aptitud(trabajador, labor, fecha):
        apto_habilidades = trabajador.tiene_habilidades(labor.get_habilidades_requeridas())
        apto_credenciales_labor = trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha)
        apto_credenciales_area = trabajador.tiene_credenciales_activas(labor.get_area().get_credenciales_obligatorias(), fecha)

        if not (apto_habilidades and apto_credenciales_labor and apto_credenciales_area):
            habilidades_faltantes = trabajador.obtener_habilidades_faltantes(labor.get_habilidades_requeridas())
            credenciales_faltantes = trabajador.obtener_credenciales_faltantes(
                labor.get_credenciales_requeridas(), fecha
            ) | trabajador.obtener_credenciales_faltantes(labor.get_area().get_credenciales_obligatorias(), fecha)

            partes = []
            if habilidades_faltantes:
                partes.append(f"habilidades {sorted(habilidades_faltantes)}")
            if credenciales_faltantes:
                partes.append(f"credenciales {sorted(credenciales_faltantes)}")
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no es apto para la labor '{labor.get_titulo()}': le faltan " + " y ".join(partes),
                habilidades_faltantes=habilidades_faltantes,
                credenciales_faltantes=credenciales_faltantes,
            )

        if not trabajador.puede_tomar_horas(labor.get_duracion_horas()):
            raise HorasMaximasExcedidasError(
                f"{trabajador.get_nombre()} superaria sus horas maximas semanales ({trabajador.get_horas_maximas_semana()}hs)"
            )

    @staticmethod
    def contar_ocupantes(asignaciones_existentes, franja, area, fecha):
        return sum(
            1
            for asignacion in asignaciones_existentes
            if asignacion.get_franja() == franja and asignacion.get_labor().get_area() == area and asignacion.get_fecha() == fecha
        )

    @staticmethod
    def validar_apto(trabajador, labor, franja, fecha, asignaciones_existentes):
        Asignacion.evaluar_aptitud(trabajador, labor, fecha)

        ocupantes = Asignacion.contar_ocupantes(asignaciones_existentes, franja, labor.get_area(), fecha)
        if ocupantes >= franja.get_capacidad():
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

    def guardar(self, repo):
        repo.create(
            id=f"{self.trabajador.get_id()}|{self.labor.get_id()}|{self.franja.get_nombre()}|{self.fecha.isoformat()}",
            trabajador_id=self.trabajador.get_id(),
            labor_id=self.labor.get_id(),
            franja=self.franja.get_nombre(),
            fecha=self.fecha.isoformat(),
            estado=self.estado,
        )

    @staticmethod
    def cargar_todas(repo, trabajadores_por_id, labores_por_id):
        # se reconstruyen con el constructor real (vuelve a correr validar_apto), para no
        # poder tener nunca una Asignacion persistida que sea invalida
        asignaciones = []
        for fila in repo.find_all():
            trabajador = trabajadores_por_id[int(fila["trabajador_id"])]
            labor = labores_por_id[int(fila["labor_id"])]
            franja = labor.get_area().buscar_franja(fila["franja"])
            fecha = date.fromisoformat(fila["fecha"])
            asignacion = Asignacion(trabajador, labor, franja, fecha, asignaciones, estado=fila["estado"])
            asignaciones.append(asignacion)
        return asignaciones
