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

    def get_trabajadores(self):
        return self._trabajadores

    def buscar_trabajador_por_id(self, id):
        trabajadores_por_id = {}
        for trabajador in self._trabajadores:
            trabajadores_por_id[trabajador.get_id()] = trabajador
        return trabajadores_por_id.get(id)

    def set_trabajadores(self, trabajadores):
        self._trabajadores = trabajadores

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
        return nuevo_trabajador

    def ejecutar_acciones_semanales(self):
        self._procesar_solicitudes_pendientes()
        self._reiniciar_horas_trabajadores()

    def _procesar_solicitudes_pendientes(self):
        while not self._solicitudes_pendientes.esta_vacia():
            trabajador, labor, franja, fecha = self._solicitudes_pendientes.desencolar()
            try:
                nueva_asignacion = Asignacion.crear(trabajador, labor, franja, fecha, self._asignaciones)
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
                    sugerencia = Asignacion.crear(candidato, labor, franja, fecha, self._asignaciones, estado=EstadoAsignacion.AUTOMATICA)
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

from datetime import date
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from franja import Franja
from labor import Labor
from area_de_trabajo import AreaDeTrabajo


def _armar_sistema():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=2)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    sistema = Sistema(trabajadores=[trabajador], areas=[area], labores=[labor])
    return sistema, trabajador, labor, franja


def test_buscar_trabajadores_disponibles_encuentra_apto():
    sistema, trabajador, labor, franja = _armar_sistema()
    disponibles = sistema.buscar_trabajadores_disponibles(labor, franja, date(2026, 1, 1))
    assert disponibles == [trabajador]


def test_generar_sugerencias_crea_asignacion_sugerida():
    sistema, trabajador, labor, franja = _armar_sistema()
    sugerencias = sistema.generar_sugerencias(date(2026, 1, 1))
    assert len(sugerencias) == 1
    assert sugerencias[0].get_estado() == EstadoAsignacion.AUTOMATICA
    assert sugerencias[0].get_trabajador() == trabajador
    assert trabajador.get_horas_asignadas() == labor.get_duracion_horas()


def test_generar_sugerencias_no_sobreasigna_mismo_trabajador_en_una_corrida():
    habilidad = Habilidad("Coccion")
    franja_manana = Franja("Manana", capacidad=5)
    franja_tarde = Franja("Tarde", capacidad=5)
    area = AreaDeTrabajo("Cocina", [], [franja_manana, franja_tarde])
    requisito = [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)]
    labor_1 = Labor(1, "Cocinar", "Cocinar el menu", 4, requisito, [], area)
    labor_2 = Labor(2, "Limpiar", "Limpiar la cocina", 4, requisito, [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 6)
    sistema = Sistema(trabajadores=[trabajador], areas=[area], labores=[labor_1, labor_2])
    sugerencias = sistema.generar_sugerencias(date(2026, 1, 1))
    assert len(sugerencias) == 1
    assert trabajador.get_horas_asignadas() == 4


def test_ciclo_semanal_descarta_sugeridas_y_regenera():
    sistema, trabajador, labor, franja = _armar_sistema()
    sistema.generar_sugerencias(date(2026, 1, 1))
    nuevas = sistema.ciclo_semanal(date(2026, 1, 2))
    assert len(sistema.obtener_asignaciones()) == 1
    assert len(nuevas) == 1
    assert trabajador.get_horas_asignadas() == labor.get_duracion_horas()


def test_ciclo_semanal_borra_tambien_las_aprobadas():
    sistema, trabajador, labor, franja = _armar_sistema()
    aprobada = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    aprobada.aprobar()
    sistema.obtener_asignaciones().append(aprobada)
    sistema.ciclo_semanal(date(2026, 1, 2))
    assert aprobada not in sistema.obtener_asignaciones()


def test_sistema_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    import pytest

    with pytest.raises(TypeError):
        Sistema(trabajadores=["no es trabajador"])
    with pytest.raises(TypeError):
        Sistema(areas=["no es area"])
    with pytest.raises(TypeError):
        Sistema(labores=["no es labor"])


def test_registrar_personal_con_atributos_opcionales():
    sistema, _, _, _ = _armar_sistema()
    nuevo = sistema.registrar_personal(id=5, nombre="Diego", horas_max=15, idioma="Ingles")
    assert nuevo.get_atributo("idioma") == "Ingles"
    assert nuevo in sistema.get_trabajadores()


def test_buscar_trabajador_por_id():
    sistema, trabajador, _, _ = _armar_sistema()
    assert sistema.buscar_trabajador_por_id(trabajador.get_id()) == trabajador
    assert sistema.buscar_trabajador_por_id(999) is None


def test_generar_sugerencias_omite_candidato_con_asignacion_duplicada():
    sistema, trabajador, labor, franja = _armar_sistema()
    existente = Asignacion.crear(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(existente)
    sugerencias = sistema.generar_sugerencias(date(2026, 1, 1))
    assert sugerencias == []


def test_solicitar_asignacion_duplicada_en_la_cola_lanza_error():
    import pytest

    sistema, trabajador, labor, franja = _armar_sistema()
    fecha = date(2026, 1, 1)
    sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    with pytest.raises(AsignacionDuplicadaError):
        sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    assert len(sistema.get_solicitudes_pendientes()) == 1


def test_ciclo_semanal_prioriza_solicitud_del_trabajador_sobre_sugerencia_automatica():
    sistema, trabajador, labor, franja = _armar_sistema()
    fecha = date(2026, 1, 1)
    sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    sistema.ciclo_semanal(fecha)
    asignaciones_del_trabajador = list(filter(lambda a: a.get_trabajador() == trabajador, sistema.obtener_asignaciones()))
    assert len(asignaciones_del_trabajador) == 1
    coincide_hueco = lambda a: a.get_labor() == labor and a.get_franja() == franja and a.get_fecha() == fecha
    assert len(list(filter(coincide_hueco, sistema.obtener_asignaciones()))) == 1
