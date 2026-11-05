from contextlib import nullcontext
from datetime import date
from unittest.mock import MagicMock

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
from franja import Franja, TipoFranja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from trabajador import Trabajador


def armar_escenario():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=1)
    area = AreaDeTrabajo("Cocina", [], [franja])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)], [], area)
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(habilidad, NivelHabilidad.BASICO)], [], 20)
    return trabajador, labor, franja


def test_asignacion_tipo_o_estado_invalido_lanza_error():
    trabajador, labor, franja = armar_escenario()
    with pytest.raises(TypeError):
        Asignacion("no es trabajador", labor, franja, date(2026, 1, 1), [])
    with pytest.raises(ValueError):
        Asignacion(trabajador, labor, franja, date(2026, 1, 1), [], estado="Invalido")


def test_crear_asignacion_exitosa_queda_pendiente():
    trabajador, labor, franja = armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    assert asignacion is not None
    assert asignacion.get_estado() == EstadoAsignacion.PENDIENTE
    assert trabajador.get_horas_asignadas() == 4


def test_crear_asignacion_la_agenda_en_el_trabajador():
    trabajador, labor, franja = armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    assert trabajador.get_agenda().recorrer() == [asignacion]


def test_validar_apto_informa_brecha_de_habilidades_y_credenciales_sin_repetidos():
    habilidad = Habilidad("Coccion")
    franja = Franja("Manana", capacidad=1)
    area = AreaDeTrabajo("Cocina", ["Carnet Sanitario", "NDA"], [franja])
    labor = Labor(
        1, "Cocinar", "Cocinar el menu", 4,
        [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)],
        ["Carnet Sanitario"],
        area,
    )
    trabajador = Trabajador(1, "Ana", [], [], 20)

    with pytest.raises(TrabajadorNoAptoError) as excinfo:
        Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])

    assert excinfo.value.habilidades_faltantes == {"Coccion"}
    assert excinfo.value.credenciales_faltantes == {"Carnet Sanitario", "NDA"}


def test_validar_apto_falla_si_franja_no_tiene_lugar():
    trabajador, labor, franja = armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [HabilidadDeTrabajador(Habilidad("Coccion"), NivelHabilidad.BASICO)], [], 20)
    ocupante = Asignacion(otro_trabajador, labor, franja, date(2026, 1, 1), [])
    with pytest.raises(FranjaSinLugarError):
        Asignacion.validar_apto(trabajador, labor, franja, date(2026, 1, 1), [ocupante])


def test_contar_ocupantes_cuenta_solo_la_franja_area_y_fecha_exactas():
    trabajador, labor, franja = armar_escenario()
    otra_franja = Franja("Tarde", capacidad=1)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])

    assert Asignacion.contar_ocupantes([asignacion], franja, labor.get_area(), date(2026, 1, 1)) == 1
    assert Asignacion.contar_ocupantes([asignacion], otra_franja, labor.get_area(), date(2026, 1, 1)) == 0
    assert Asignacion.contar_ocupantes([asignacion], franja, labor.get_area(), date(2026, 1, 2)) == 0


def test_crear_lanza_asignacion_duplicada_error():
    trabajador, labor, _ = armar_escenario()
    franja_grande = Franja("Manana", capacidad=5)
    primera = Asignacion(trabajador, labor, franja_grande, date(2026, 1, 1), [])
    with pytest.raises(AsignacionDuplicadaError):
        Asignacion(trabajador, labor, franja_grande, date(2026, 1, 1), [primera])


def test_reasignar_pendiente_cambia_trabajador():
    trabajador, labor, franja = armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [HabilidadDeTrabajador(Habilidad("Coccion"), NivelHabilidad.BASICO)], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.reasignar(otro_trabajador)
    assert asignacion.get_trabajador() == otro_trabajador
    assert trabajador.get_horas_asignadas() == 0
    assert otro_trabajador.get_horas_asignadas() == 4
    assert trabajador.get_agenda().recorrer() == []
    assert otro_trabajador.get_agenda().recorrer() == [asignacion]


def test_reasignar_a_trabajador_no_apto_lanza_error():
    trabajador, labor, franja = armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    with pytest.raises(TrabajadorNoAptoError):
        asignacion.reasignar(otro_trabajador)
    assert asignacion.get_trabajador() == trabajador


def test_rechazar_libera_horas():
    trabajador, labor, franja = armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.rechazar()
    assert trabajador.get_horas_asignadas() == 0
    assert trabajador.get_agenda().recorrer() == []


def test_rechazar_aprobada_lanza_value_error():
    trabajador, labor, franja = armar_escenario()
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.aprobar()
    with pytest.raises(ValueError):
        asignacion.rechazar()


def test_reasignar_aprobada_lanza_value_error():
    trabajador, labor, franja = armar_escenario()
    otro_trabajador = Trabajador(2, "Beto", [], [], 20)
    asignacion = Asignacion(trabajador, labor, franja, date(2026, 1, 1), [])
    asignacion.aprobar()
    with pytest.raises(ValueError):
        asignacion.reasignar(otro_trabajador)


# ---------------------------------------------------------------------------
# Test grande: validar_apto es LA decision de negocio de todo el TP.
#
# No es un CRUD generico: es la regla propia de "Gestion de Capacidades
# Inteligente" que decide, en un unico lugar, si un trabajador puede ocupar
# una labor+franja+fecha, combinando 6 condiciones independientes (R4, R5,
# R6, R7 de la consigna) y traduciendo cada violacion a su excepcion propia.
#
# Mockeamos al Trabajador (con spec=Trabajador, para pasar el isinstance()
# que exige Asignacion al validar) para poder prender y apagar cada condicion
# por separado sin depender de la logica real de Habilidad/CredencialProfesional.
# Como tiene_credenciales_activas se llama dos veces con argumentos distintos
# (credenciales de la labor vs. del area), el side_effect distingue por
# identidad de la lista cual de las dos credenciales le estan pidiendo.
# ---------------------------------------------------------------------------

@pytest.fixture
def labor_con_requisitos():
    habilidad = Habilidad("Python")
    franja = Franja(TipoFranja.MANIANA, capacidad=2)
    area = AreaDeTrabajo("Backend", ["NDA Firmado"], [franja])
    labor = Labor(
        1, "Armar API", "Escribir un endpoint nuevo", 4,
        [HabilidadRequerida(habilidad, NivelHabilidad.BASICO)],
        ["Certificado Python"],
        area,
    )
    return labor, franja


def mockear_trabajador(labor, apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas):
    trabajador_mock = MagicMock(spec=Trabajador)
    trabajador_mock.get_nombre.return_value = "Mockeado"
    trabajador_mock.tiene_habilidades.return_value = apto_habilidades
    trabajador_mock.puede_tomar_horas.return_value = puede_tomar_horas

    credenciales_de_la_labor = labor.get_credenciales_requeridas()
    credenciales_del_area = labor.get_area().get_credenciales_obligatorias()

    def responder_credenciales(credenciales_pedidas, fecha):
        if credenciales_pedidas is credenciales_de_la_labor:
            return apto_credenciales_labor
        if credenciales_pedidas is credenciales_del_area:
            return apto_credenciales_area
        raise AssertionError("validar_apto pidio credenciales que no reconozco")

    trabajador_mock.tiene_credenciales_activas.side_effect = responder_credenciales
    return trabajador_mock


def mockear_asignacion_existente(labor, franja, fecha):
    asignacion_mock = MagicMock(spec=Asignacion)
    asignacion_mock.get_labor.return_value = labor
    asignacion_mock.get_franja.return_value = franja
    asignacion_mock.get_fecha.return_value = fecha
    return asignacion_mock


@pytest.mark.parametrize(
    "apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas, "
    "franja_ocupada, hay_asignacion_previa, excepcion_esperada",
    [
        pytest.param(True, True, True, True, False, False, None, id="cumple_las_6_reglas"),
        pytest.param(False, True, True, True, False, False, TrabajadorNoAptoError, id="sin_habilidad_requerida"),
        pytest.param(True, False, True, True, False, False, TrabajadorNoAptoError, id="sin_credencial_de_la_labor"),
        pytest.param(True, True, False, True, False, False, TrabajadorNoAptoError, id="sin_credencial_obligatoria_del_area"),
        pytest.param(True, True, True, False, False, False, HorasMaximasExcedidasError, id="supera_horas_maximas_semanales"),
        pytest.param(True, True, True, True, True, False, FranjaSinLugarError, id="franja_sin_lugar_disponible"),
        pytest.param(True, True, True, True, False, True, AsignacionDuplicadaError, id="ya_hay_asignacion_en_ese_hueco"),
    ],
)
def test_validar_apto_aplica_las_6_reglas_de_negocio_de_forma_independiente(
    labor_con_requisitos,
    apto_habilidades,
    apto_credenciales_labor,
    apto_credenciales_area,
    puede_tomar_horas,
    franja_ocupada,
    hay_asignacion_previa,
    excepcion_esperada,
):
    labor, franja = labor_con_requisitos
    fecha = date(2026, 1, 1)

    trabajador_mock = mockear_trabajador(
        labor, apto_habilidades, apto_credenciales_labor, apto_credenciales_area, puede_tomar_horas
    )

    asignaciones_existentes = []
    if franja_ocupada:
        # tantos ocupantes como la capacidad, para dejarla justo sin lugar
        asignaciones_existentes = [mockear_asignacion_existente(labor, franja, fecha) for _ in range(franja.get_capacidad())]
    if hay_asignacion_previa:
        asignaciones_existentes = [mockear_asignacion_existente(labor, franja, fecha)]

    contexto = pytest.raises(excepcion_esperada) if excepcion_esperada else nullcontext()
    with contexto:
        Asignacion.validar_apto(trabajador_mock, labor, franja, fecha, asignaciones_existentes)
