from datetime import date

import pytest

from area_de_trabajo import AreaDeTrabajo
from asignacion import Asignacion, AsignacionDuplicadaError, EstadoAsignacion
from franja import Franja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from sistema import Sistema
from trabajador import Trabajador


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
    aprobada = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    aprobada.aprobar()
    sistema.obtener_asignaciones().append(aprobada)
    sistema.ciclo_semanal(date(2026, 1, 2))
    assert aprobada not in sistema.obtener_asignaciones()


def test_sistema_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
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


def test_buscar_trabajador_por_id_se_actualiza_automaticamente_al_registrar():
    sistema, _, _, _ = _armar_sistema()
    nuevo = sistema.registrar_personal(id=7, nombre="Diego", horas_max=15)
    assert sistema.buscar_trabajador_por_id(7) == nuevo


def test_buscar_trabajador_por_id_se_actualiza_al_hacer_set_trabajadores():
    sistema, _, _, _ = _armar_sistema()
    otro = Trabajador(99, "Beto", [], [], 20)
    sistema.set_trabajadores([otro])
    assert sistema.buscar_trabajador_por_id(99) == otro
    assert sistema.buscar_trabajador_por_id(1) is None


def test_generar_sugerencias_omite_candidato_con_asignacion_duplicada():
    sistema, trabajador, labor, franja = _armar_sistema()
    existente = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(existente)
    sugerencias = sistema.generar_sugerencias(date(2026, 1, 1))
    assert sugerencias == []


def test_solicitar_asignacion_duplicada_en_la_cola_lanza_error():
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
