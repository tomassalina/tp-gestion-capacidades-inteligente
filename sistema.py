from asignacion import Asignacion, EstadoAsignacion, TrabajadorNoAptoError, HorasMaximasExcedidasError, FranjaSinLugarError, AsignacionDuplicadaError
from trabajador import Trabajador
from area_de_trabajo import AreaDeTrabajo
from labor import Labor
from cola import Cola

ERRORES_ASIGNACION = (TrabajadorNoAptoError, HorasMaximasExcedidasError, FranjaSinLugarError, AsignacionDuplicadaError)


class Sistema:

    def __init__(self, trabajadores=None, areas=None, labores=None):
        if trabajadores is not None and (not isinstance(trabajadores, list) or not all(map(lambda t: isinstance(t, Trabajador), trabajadores))):
            raise TypeError("trabajadores debe ser una lista de Trabajador")
        if areas is not None and (not isinstance(areas, list) or not all(map(lambda a: isinstance(a, AreaDeTrabajo), areas))):
            raise TypeError("areas debe ser una lista de AreaDeTrabajo")
        if labores is not None and (not isinstance(labores, list) or not all(map(lambda l: isinstance(l, Labor), labores))):
            raise TypeError("labores debe ser una lista de Labor")
        self._trabajadores = trabajadores or []
        self._areas = areas or []
        self._labores = labores or []
        self._solicitudes_pendientes, self._asignaciones = Cola(), []
        self._trabajadores_por_id = {}
        self._reindexar_trabajadores()

    def get_trabajadores(self):
        return self._trabajadores

    def _reindexar_trabajadores(self):
        self._trabajadores_por_id = {}
        for trabajador in self._trabajadores:
            self._trabajadores_por_id[trabajador.get_id()] = trabajador

    def buscar_trabajador_por_id(self, id):
        return self._trabajadores_por_id.get(id)

    def set_trabajadores(self, trabajadores):
        self._trabajadores = trabajadores
        self._reindexar_trabajadores()

    def get_areas(self):
        return self._areas

    def set_areas(self, areas):
        self._areas = areas

    def get_labores(self):
        return self._labores

    def set_labores(self, labores):
        self._labores = labores

    def obtener_asignaciones(self):
        return self._asignaciones

    def get_solicitudes_pendientes(self):
        return self._solicitudes_pendientes

    def solicitar_asignacion(self, trabajador, labor, franja, fecha):
        if trabajador not in self.buscar_trabajadores_disponibles(labor, franja, fecha):
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no es apto para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}'"
            )
        if self._ya_esta_en_la_cola(trabajador, labor, franja, fecha):
            raise AsignacionDuplicadaError(
                f"{trabajador.get_nombre()} ya tiene una solicitud pendiente para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}' el {fecha}"
            )
        self._solicitudes_pendientes.encolar((trabajador, labor, franja, fecha))

    def _ya_esta_en_la_cola(self, trabajador, labor, franja, fecha):
        for solicitud in self._solicitudes_pendientes.recorrer():
            trabajador_en_cola, labor_en_cola, franja_en_cola, fecha_en_cola = solicitud
            if trabajador_en_cola == trabajador and labor_en_cola == labor and franja_en_cola == franja and fecha_en_cola == fecha:
                return True
        return False

    def registrar_personal(self, id, nombre, horas_max, **atributos):
        nuevo_trabajador = Trabajador(
            id=id,
            nombre=nombre,
            habilidades=[],
            credenciales=[],
            horas_maximas_semana=horas_max,
            **atributos,
        )
        self._trabajadores.append(nuevo_trabajador)
        self._trabajadores_por_id[nuevo_trabajador.get_id()] = nuevo_trabajador
        return nuevo_trabajador

    def ejecutar_acciones_semanales(self):
        self._procesar_solicitudes_pendientes()
        self._reiniciar_horas_trabajadores()

    def _procesar_solicitudes_pendientes(self):
        while not self._solicitudes_pendientes.esta_vacia():
            trabajador, labor, franja, fecha = self._solicitudes_pendientes.desencolar()
            try:
                nueva_asignacion = Asignacion(trabajador, labor, franja, fecha, self._asignaciones)
            except ERRORES_ASIGNACION as e:
                print(f"No se pudo procesar la solicitud de {trabajador.get_nombre()} para '{labor.get_titulo()}': {e}")
            else:
                self._asignaciones.append(nueva_asignacion)

    def _reiniciar_horas_trabajadores(self):
        for trabajador in self._trabajadores:
            trabajador.reiniciar_horas()

    def _tiene_asignacion_aprobada(self, labor, franja, fecha):
        for asignacion in self._asignaciones:
            if asignacion.get_labor() == labor and asignacion.get_franja() == franja and asignacion.get_fecha() == fecha:
                if asignacion.get_estado() == EstadoAsignacion.APROBADA:
                    return True
        return False

    def buscar_trabajadores_disponibles(self, labor, franja, fecha):
        candidatos = []
        for trabajador in self._trabajadores:
            apto_habilidades = trabajador.tiene_habilidades(labor.get_habilidades_requeridas())
            apto_credenciales_labor = trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha)
            apto_credenciales_area = trabajador.tiene_credenciales_activas(labor.get_area().get_credenciales_obligatorias(), fecha)
            if not (apto_habilidades and apto_credenciales_labor and apto_credenciales_area):
                continue
            if not trabajador.puede_tomar_horas(labor.get_duracion_horas()):
                continue
            if not franja.tiene_lugar():
                continue
            if self._tiene_asignacion_aprobada(labor, franja, fecha):
                continue
            candidatos.append(trabajador)
        return candidatos

    def generar_sugerencias(self, fecha):
        nuevas_sugerencias = []
        for labor in self._labores:
            for franja in labor.get_area().get_franjas():
                if self._tiene_asignacion_aprobada(labor, franja, fecha):
                    continue
                candidatos = self.buscar_trabajadores_disponibles(labor, franja, fecha)
                if len(candidatos) == 0:
                    continue
                candidato = candidatos[0]
                try:
                    sugerencia = Asignacion(candidato, labor, franja, fecha, self._asignaciones, estado=EstadoAsignacion.AUTOMATICA)
                except ERRORES_ASIGNACION as e:
                    print(f"No se pudo generar sugerencia para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}': {e}")
                else:
                    self._asignaciones.append(sugerencia)
                    nuevas_sugerencias.append(sugerencia)
        return nuevas_sugerencias

    def ciclo_semanal(self, fecha):
        self._asignaciones = []
        self._reiniciar_horas_trabajadores()
        self._procesar_solicitudes_pendientes()
        return self.generar_sugerencias(fecha)
