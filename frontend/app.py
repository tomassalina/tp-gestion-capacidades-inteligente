"""Frontend Streamlit para el TP de Gestion de Capacidades Inteligente.

Este modulo NO reimplementa ninguna regla de negocio: todo el trabajo real
(validaciones, asignaciones, aprobaciones, etc.) lo hacen las clases del
directorio padre (Sistema, Supervisor, Trabajador, etc.). Esta app solo arma
la interfaz y llama a los metodos publicos de esas clases.
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from area_de_trabajo import AreaDeTrabajo
from asignacion import EstadoAsignacion
from credencial_profesional import CredencialProfesional
from franja import Franja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador

NOMBRES_NIVEL = {
    NivelHabilidad.BASICO: "Basico",
    NivelHabilidad.INTERMEDIO: "Intermedio",
    NivelHabilidad.AVANZADO: "Avanzado",
}


def seed_sistema() -> tuple[Sistema, Supervisor]:
    """Arma datos de ejemplo, en la misma linea que main.py, para que la UI
    nunca arranque vacia."""
    habilidad_coccion = Habilidad("Coccion")

    franja_manana = Franja("Manana", capacidad=1)
    franja_tarde = Franja("Tarde", capacidad=2)
    franja_noche = Franja("Noche", capacidad=1)

    area_cocina = AreaDeTrabajo(
        nombre="Cocina",
        credenciales_obligatorias=["Carnet de Manipulacion de Alimentos"],
        franjas=[franja_manana, franja_tarde, franja_noche],
    )

    credencial_vigente = CredencialProfesional(
        nombre="Carnet de Manipulacion de Alimentos",
        fecha_obtencion=date(2025, 1, 1),
        fecha_caducidad=date(2027, 1, 1),
    )
    credencial_vencida = CredencialProfesional(
        nombre="Carnet de Manipulacion de Alimentos",
        fecha_obtencion=date(2020, 1, 1),
        fecha_caducidad=date(2021, 1, 1),
    )

    ana = Trabajador(
        id=1,
        nombre="Ana",
        habilidades=[HabilidadDeTrabajador(habilidad_coccion, NivelHabilidad.AVANZADO)],
        credenciales=[credencial_vigente],
        horas_maximas_semana=20,
    )
    beto = Trabajador(
        id=2,
        nombre="Beto",
        habilidades=[HabilidadDeTrabajador(habilidad_coccion, NivelHabilidad.INTERMEDIO)],
        credenciales=[credencial_vencida],
        horas_maximas_semana=20,
    )

    labor_cocinar = Labor(
        id=1,
        titulo="Preparar almuerzo",
        descripcion="Cocinar el menu del dia",
        duracion_horas=4,
        habilidades_requeridas=[HabilidadRequerida(habilidad_coccion, NivelHabilidad.INTERMEDIO)],
        credenciales_requeridas=["Carnet de Manipulacion de Alimentos"],
        area=area_cocina,
    )

    carla = Supervisor(
        id=3,
        nombre="Carla",
        habilidades=[],
        credenciales=[],
        horas_maximas_semana=20,
    )

    sistema = Sistema(trabajadores=[ana, beto, carla], areas=[area_cocina], labores=[labor_cocinar])
    return sistema, carla


if "sistema" not in st.session_state:
    st.session_state.sistema, st.session_state.supervisor = seed_sistema()
if "atributos_rows" not in st.session_state:
    st.session_state.atributos_rows = []
if "atributos_counter" not in st.session_state:
    st.session_state.atributos_counter = 0

sistema: Sistema = st.session_state.sistema
supervisor: Supervisor = st.session_state.supervisor

st.set_page_config(page_title="Gestion de Capacidades", layout="wide")
st.title("Gestion de Capacidades Inteligente")

tab_personal, tab_areas, tab_asignaciones, tab_reglas = st.tabs(
    ["Personal", "Areas y Labores", "Asignaciones", "Reglas"]
)

# ---------------------------------------------------------------------------
# Tab 1: Personal
# ---------------------------------------------------------------------------
with tab_personal:
    st.subheader("Personal registrado")

    filas = []
    for trabajador in sistema.get_trabajadores():
        filas.append(
            {
                "ID": trabajador.get_id(),
                "Nombre": trabajador.get_nombre(),
                "Rol": "Supervisor" if isinstance(trabajador, Supervisor) else "Trabajador",
                "Horas asignadas": trabajador.get_horas_asignadas(),
                "Horas maximas": trabajador.get_horas_maximas_semana(),
                "Habilidades": ", ".join(
                    f"{h.get_habilidad().get_nombre()} ({NOMBRES_NIVEL.get(h.get_nivel(), h.get_nivel())})"
                    for h in trabajador.get_habilidades()
                )
                or "-",
                "Credenciales": ", ".join(c.get_nombre() for c in trabajador.get_credenciales()) or "-",
                "Atributos": ", ".join(f"{k}={v}" for k, v in trabajador.get_atributos().items()) or "-",
            }
        )
    st.dataframe(filas, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Registrar nuevo trabajador")
    st.caption(
        "Los atributos adicionales se pasan como **kwargs a `sistema.registrar_personal(...)`."
    )

    col1, col2, col3 = st.columns(3)
    nuevo_id = col1.number_input("ID", min_value=1, step=1, key="nuevo_id")
    nuevo_nombre = col2.text_input("Nombre", key="nuevo_nombre")
    nuevo_horas_max = col3.number_input("Horas maximas semanales", min_value=1, step=1, key="nuevo_horas_max")

    st.caption("Atributos libres (clave/valor)")
    for fila in list(st.session_state.atributos_rows):
        fila_id = fila["id"]
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.text_input("Clave", key=f"attr_clave_{fila_id}")
        c2.text_input("Valor", key=f"attr_valor_{fila_id}")
        if c3.button("Quitar", key=f"attr_quitar_{fila_id}"):
            st.session_state.atributos_rows = [
                f for f in st.session_state.atributos_rows if f["id"] != fila_id
            ]
            st.rerun()

    if st.button("+ Agregar atributo"):
        st.session_state.atributos_counter += 1
        st.session_state.atributos_rows.append({"id": st.session_state.atributos_counter})
        st.rerun()

    if st.button("Registrar trabajador", type="primary"):
        atributos = {}
        for fila in st.session_state.atributos_rows:
            clave = st.session_state.get(f"attr_clave_{fila['id']}", "").strip()
            valor = st.session_state.get(f"attr_valor_{fila['id']}", "")
            if clave:
                atributos[clave] = valor
        try:
            nuevo = sistema.registrar_personal(
                int(nuevo_id), nuevo_nombre, int(nuevo_horas_max), **atributos
            )
            st.session_state.atributos_rows = []
            st.success(f"Trabajador '{nuevo.get_nombre()}' registrado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

# ---------------------------------------------------------------------------
# Tab 2: Areas y Labores
# ---------------------------------------------------------------------------
with tab_areas:
    st.subheader("Areas de trabajo")
    for area in sistema.get_areas():
        with st.expander(f"Area: {area.get_nombre()}", expanded=True):
            st.write("**Credenciales obligatorias:**", ", ".join(area.get_credenciales_obligatorias()) or "-")
            franjas_info = [
                {
                    "Franja": franja.get_nombre(),
                    "Capacidad": franja.get_capacidad(),
                    "Ocupados": franja.get_trabajadores_asignados(),
                    "Tiene lugar": franja.tiene_lugar(),
                }
                for franja in area.get_franjas()
            ]
            st.dataframe(franjas_info, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Labores")
    for labor in sistema.get_labores():
        with st.expander(f"Labor: {labor.get_titulo()}", expanded=True):
            st.write(labor.get_descripcion())
            st.write("**Duracion:**", labor.get_duracion_horas(), "horas")
            st.write("**Area:**", labor.get_area().get_nombre())
            habilidades = ", ".join(
                f"{h.get_habilidad().get_nombre()} (min. {NOMBRES_NIVEL.get(h.get_nivel_minimo(), h.get_nivel_minimo())})"
                for h in labor.get_habilidades_requeridas()
            )
            st.write("**Habilidades requeridas:**", habilidades or "-")
            st.write("**Credenciales requeridas:**", ", ".join(labor.get_credenciales_requeridas()) or "-")

# ---------------------------------------------------------------------------
# Tab 3: Asignaciones
# ---------------------------------------------------------------------------
with tab_asignaciones:
    st.subheader("Acciones del sistema")
    fecha_accion = st.date_input("Fecha", value=date.today(), key="fecha_accion")

    col1, col2 = st.columns(2)
    if col1.button("Generar sugerencias"):
        try:
            sugerencias = sistema.generar_sugerencias(fecha_accion)
            st.success(f"Se generaron {len(sugerencias)} sugerencia(s).")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    if col2.button("Ejecutar ciclo semanal"):
        try:
            nuevas = sistema.ciclo_semanal(fecha_accion)
            st.success(f"Ciclo semanal ejecutado. Nuevas sugerencias: {len(nuevas)}.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    with st.expander("Flujo manual: solicitar asignacion y procesarla"):
        trabajadores = sistema.get_trabajadores()
        labores = sistema.get_labores()
        if trabajadores and labores:
            id_trabajador_sel = st.selectbox(
                "Trabajador", [t.get_id() for t in trabajadores],
                format_func=lambda tid: next(t.get_nombre() for t in trabajadores if t.get_id() == tid),
                key="sol_trabajador",
            )
            t_sel = next(t for t in trabajadores if t.get_id() == id_trabajador_sel)
            id_labor_sel = st.selectbox(
                "Labor", [l.get_id() for l in labores],
                format_func=lambda lid: next(l.get_titulo() for l in labores if l.get_id() == lid),
                key="sol_labor",
            )
            l_sel = next(l for l in labores if l.get_id() == id_labor_sel)
            franjas_area = l_sel.get_area().get_franjas()
            if franjas_area:
                nombre_franja_sel = st.selectbox(
                    "Franja", [f.get_nombre() for f in franjas_area], key="sol_franja"
                )
                f_sel = next(f for f in franjas_area if f.get_nombre() == nombre_franja_sel)
            else:
                f_sel = None
            fecha_sol = st.date_input("Fecha de la solicitud", value=date.today(), key="sol_fecha")
            if st.button("Solicitar asignacion", disabled=f_sel is None):
                sistema.solicitar_asignacion(t_sel, l_sel, f_sel, fecha_sol)
                st.success("Solicitud agregada a la cola de pendientes.")
            if st.button("Procesar solicitudes pendientes (supervisor)"):
                supervisor.ejecutar_acciones_del_sistema(sistema)
                st.success("Solicitudes procesadas y horas semanales reiniciadas.")
                st.rerun()
        else:
            st.info("Hace falta al menos un trabajador y una labor para solicitar una asignacion.")

    st.divider()
    st.subheader("Asignaciones")

    estados_disponibles = [EstadoAsignacion.SUGERIDA, EstadoAsignacion.PENDIENTE, EstadoAsignacion.APROBADA]
    filtro_estado = st.multiselect("Filtrar por estado", estados_disponibles, default=estados_disponibles)

    asignaciones = [a for a in sistema.obtener_asignaciones() if a.get_estado() in filtro_estado]

    if not asignaciones:
        st.info("No hay asignaciones para los filtros seleccionados.")

    for i, asignacion in enumerate(asignaciones):
        with st.container(border=True):
            st.write(
                f"**{asignacion.get_trabajador().get_nombre()}** -> "
                f"**{asignacion.get_labor().get_titulo()}** "
                f"en franja '{asignacion.get_franja().get_nombre()}' "
                f"el {asignacion.get_fecha()} — estado: **{asignacion.get_estado()}**"
            )

            if asignacion.get_estado() in (EstadoAsignacion.SUGERIDA, EstadoAsignacion.PENDIENTE):
                c1, c2, c3 = st.columns([1, 2, 1])
                if c1.button("Aprobar", key=f"aprobar_{i}"):
                    try:
                        supervisor.aprobar_asignacion(asignacion)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

                otros = [t for t in sistema.get_trabajadores() if t != asignacion.get_trabajador()]
                nuevo_trabajador = None
                if otros:
                    id_nuevo_trabajador = c2.selectbox(
                        "Reasignar a",
                        [t.get_id() for t in otros],
                        format_func=lambda tid: next(t.get_nombre() for t in otros if t.get_id() == tid),
                        key=f"reasignar_select_{i}",
                        label_visibility="collapsed",
                    )
                    nuevo_trabajador = next(t for t in otros if t.get_id() == id_nuevo_trabajador)
                if c3.button("Reasignar", key=f"reasignar_btn_{i}", disabled=nuevo_trabajador is None):
                    try:
                        supervisor.reasignar_asignacion(asignacion, nuevo_trabajador)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    if st.button("Aprobar todas las pendientes"):
        supervisor.aprobar_asignaciones_pendientes(sistema)
        st.rerun()

# ---------------------------------------------------------------------------
# Tab 4: Reglas
# ---------------------------------------------------------------------------
with tab_reglas:
    st.subheader("Agregar credencial obligatoria a un area")
    areas = sistema.get_areas()
    if areas:
        nombre_area_sel = st.selectbox(
            "Area", [a.get_nombre() for a in areas], key="regla_area"
        )
        area_sel = next(a for a in areas if a.get_nombre() == nombre_area_sel)
        credencial_nombre = st.text_input("Nombre de la credencial obligatoria", key="regla_credencial")
        if st.button("Agregar regla"):
            if credencial_nombre.strip():
                try:
                    supervisor.agregar_regla_area(area_sel, credencial_nombre.strip())
                    st.success(f"Credencial '{credencial_nombre}' agregada a '{area_sel.get_nombre()}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("El nombre de la credencial no puede estar vacio.")
    else:
        st.info("No hay areas registradas todavia.")
