from datetime import date
from unittest.mock import MagicMock

import pytest

from area_de_trabajo import AreaDeTrabajo
from asignacion import Asignacion, AsignacionDuplicadaError, EstadoAsignacion
from franja import Franja, TipoFranja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from sistema import Sistema
from trabajador import Trabajador


@pytest.fixture
def sistema_con_ana():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=2)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    sistema = Sistema(trabajadores=[trabajador], areas=[area], labores=[labor])
    return sistema, trabajador, labor, franja


def test_buscar_trabajadores_disponibles_encuentra_apto(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
    disponibles = sistema.buscar_trabajadores_disponibles(labor, franja, date(2026, 1, 1))
    assert disponibles == [trabajador]


def test_generar_sugerencias_crea_asignacion_sugerida(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
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


def test_ciclo_semanal_descarta_sugeridas_y_regenera(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
    sistema.generar_sugerencias(date(2026, 1, 1))
    nuevas = sistema.ciclo_semanal(date(2026, 1, 2))
    assert len(sistema.obtener_asignaciones()) == 1
    assert len(nuevas) == 1
    assert trabajador.get_horas_asignadas() == labor.get_duracion_horas()


def test_ciclo_semanal_borra_tambien_las_aprobadas(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
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


def test_registrar_personal_con_atributos_opcionales(sistema_con_ana):
    sistema, _, _, _ = sistema_con_ana
    nuevo = sistema.registrar_personal(id=5, nombre="Diego", horas_max=15, idioma="Ingles")
    assert nuevo.get_atributo("idioma") == "Ingles"
    assert nuevo in sistema.get_trabajadores()


def test_buscar_trabajador_por_id(sistema_con_ana):
    sistema, trabajador, _, _ = sistema_con_ana
    assert sistema.buscar_trabajador_por_id(trabajador.get_id()) == trabajador
    assert sistema.buscar_trabajador_por_id(999) is None


def test_buscar_trabajador_por_id_se_actualiza_automaticamente_al_registrar(sistema_con_ana):
    sistema, _, _, _ = sistema_con_ana
    nuevo = sistema.registrar_personal(id=7, nombre="Diego", horas_max=15)
    assert sistema.buscar_trabajador_por_id(7) == nuevo


def test_buscar_trabajador_por_id_se_actualiza_al_hacer_set_trabajadores(sistema_con_ana):
    sistema, _, _, _ = sistema_con_ana
    otro = Trabajador(99, "Beto", [], [], 20)
    sistema.set_trabajadores([otro])
    assert sistema.buscar_trabajador_por_id(99) == otro
    assert sistema.buscar_trabajador_por_id(1) is None


def test_generar_sugerencias_omite_candidato_con_asignacion_duplicada(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
    existente = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    sistema.obtener_asignaciones().append(existente)
    sugerencias = sistema.generar_sugerencias(date(2026, 1, 1))
    assert sugerencias == []


def test_solicitar_asignacion_duplicada_en_la_cola_lanza_error(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
    fecha = date(2026, 1, 1)
    sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    with pytest.raises(AsignacionDuplicadaError):
        sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    assert len(sistema.get_solicitudes_pendientes()) == 1


def test_ciclo_semanal_prioriza_solicitud_del_trabajador_sobre_sugerencia_automatica(sistema_con_ana):
    sistema, trabajador, labor, franja = sistema_con_ana
    fecha = date(2026, 1, 1)
    sistema.solicitar_asignacion(trabajador, labor, franja, fecha)
    sistema.ciclo_semanal(fecha)
    asignaciones_del_trabajador = list(filter(lambda a: a.get_trabajador() == trabajador, sistema.obtener_asignaciones()))
    assert len(asignaciones_del_trabajador) == 1
    coincide_hueco = lambda a: a.get_labor() == labor and a.get_franja() == franja and a.get_fecha() == fecha
    assert len(list(filter(coincide_hueco, sistema.obtener_asignaciones()))) == 1


# ---------------------------------------------------------------------------
# Test grande: buscar_trabajadores_disponibles aisla y combina sus 5 reglas.
#
# Mockeamos al Trabajador (con spec=Trabajador, para pasar el isinstance() que
# hace Sistema al construirse) para controlar de forma independiente cada una
# de las 5 condiciones que Sistema evalua, sin depender de la logica real de
# Trabajador/Habilidad/CredencialProfesional. Labor y AreaDeTrabajo quedan
# reales, para poder distinguir "credenciales de la labor" de "credenciales
# del area" por identidad de la lista (son getters que devuelven siempre el
# mismo objeto interno).
# ---------------------------------------------------------------------------

@pytest.fixture
def labor_con_requisitos():
    habilidad = Habilidad("Python")
    franja = Franja(TipoFranja.MANIANA, capacidad=1)
    area = AreaDeTrabajo("Backend", ["NDA Firmado"], [franja])
    labor = Labor(
        1, "Armar API", "Escribir un endpoint nuevo", 4,
        [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)],
        ["Certificado Python"],
        area,
    )
    return labor, franja


def _mockear_trabajador(labor, apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas):
    trabajador_mock = MagicMock(spec=Trabajador)
    trabajador_mock.tiene_habilidades.return_value = apto_habilidades
    trabajador_mock.puede_tomar_horas.return_value = puede_tomar_horas

    credenciales_de_la_labor = labor.get_credenciales_requeridas()
    credenciales_del_area = labor.get_area().get_credenciales_obligatorias()

    def responder_credenciales(credenciales_pedidas, fecha):
        if credenciales_pedidas is credenciales_de_la_labor:
            return apto_credenciales_labor
        if credenciales_pedidas is credenciales_del_area:
            return apto_credenciales_area
        raise AssertionError("Sistema pidio credenciales que no reconozco")

    trabajador_mock.tiene_credenciales_activas.side_effect = responder_credenciales
    return trabajador_mock


@pytest.mark.parametrize(
    "apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas, franja_ocupada, debe_aparecer",
    [
        pytest.param(True, True, True, True, False, True, id="cumple_las_5_reglas"),
        pytest.param(False, True, True, True, False, False, id="sin_habilidad_requerida"),
        pytest.param(True, False, True, True, False, False, id="sin_credencial_de_la_labor"),
        pytest.param(True, True, False, True, False, False, id="sin_credencial_obligatoria_del_area"),
        pytest.param(True, True, True, False, False, False, id="supera_horas_maximas_semanales"),
        pytest.param(True, True, True, True, True, False, id="franja_sin_lugar_disponible"),
    ],
)
def test_buscar_trabajadores_disponibles_evalua_las_5_reglas_de_forma_independiente(
    labor_con_requisitos,
    apto_habilidades,
    apto_credenciales_labor,
    apto_credenciales_area,
    puede_tomar_horas,
    franja_ocupada,
    debe_aparecer,
):
    labor, franja = labor_con_requisitos
    if franja_ocupada:
        franja.ocupar_lugar()  # capacidad=1, la deja justo sin lugar

    trabajador_mock = _mockear_trabajador(
        labor, apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas
    )
    sistema = Sistema(trabajadores=[trabajador_mock], areas=[labor.get_area()], labores=[labor])

    disponibles = sistema.buscar_trabajadores_disponibles(labor, franja, date(2026, 1, 1))

    assert (trabajador_mock in disponibles) == debe_aparecer
