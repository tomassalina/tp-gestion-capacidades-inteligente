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
from datetime import timedelta
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from credencial_profesional import CredencialProfesional
from labor import Labor
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador

NOMBRES_NIVEL = {
    NivelHabilidad.BASICO: "Basico",
    NivelHabilidad.INTERMEDIO: "Intermedio",
    NivelHabilidad.AVANZADO: "Avanzado",
}


from seed import armar_seed


if "sistema" not in st.session_state:
    st.session_state.sistema, st.session_state.supervisor = armar_seed()
if "atributos_rows" not in st.session_state:
    st.session_state.atributos_rows = []
if "atributos_counter" not in st.session_state:
    st.session_state.atributos_counter = 0

sistema: Sistema = st.session_state.sistema
supervisor: Supervisor = st.session_state.supervisor

st.set_page_config(page_title="Gestion de Capacidades", layout="wide", page_icon="🧩")
st.markdown(
    """<style>
    .block-container {padding-top: 2rem; max-width: 1200px;}
    h1 {font-weight: 800;}
    div[data-testid="stMetric"] {background: rgba(127,127,127,0.08); border-radius: 10px; padding: 12px;}
    </style>""",
    unsafe_allow_html=True,
)
st.title("🧩 Gestion de Capacidades Inteligente")
st.caption("Software Co. — asignacion inteligente de personal a labores")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Personal", len(sistema.get_trabajadores()))
m2.metric("Areas", len(sistema.get_areas()))
m3.metric("Labores", len(sistema.get_labores()))
m4.metric("Solicitudes en cola", len(sistema.get_solicitudes_pendientes()))

tab_flujo, tab_personal, tab_areas, tab_asignaciones, tab_reglas = st.tabs(
    ["Flujo Guiado", "Personal", "Areas y Labores", "Asignaciones", "Reglas"]
)

# ---------------------------------------------------------------------------
# Tab 0: Flujo Guiado
# ---------------------------------------------------------------------------
with tab_flujo:
    st.subheader("De la solicitud a la asignacion, paso a paso")
    st.caption("Seguí los pasos en orden. Cada uno usa los metodos reales de Sistema/Supervisor, nada se simula.")

    fecha_demo = st.date_input("Fecha para esta demo", value=date.today(), key="demo_fecha")
    labor_demo = sistema.get_labores()[0] if sistema.get_labores() else None
    franja_demo = labor_demo.get_area().get_franjas()[0] if labor_demo else None

    st.markdown("### Paso 1 — Arrancar desde cero")
    if st.button("Reiniciar todo (recarga los datos de ejemplo)"):
        st.session_state.sistema, st.session_state.supervisor = armar_seed()
        st.session_state.pop("demo_resultados", None)
        st.rerun()

    st.divider()
    st.markdown("### Paso 2 — Tres trabajadores piden la misma labor")
    if labor_demo and franja_demo:
        st.write(f"Labor: **{labor_demo.get_titulo()}** — Franja: **{franja_demo.get_nombre()}** — Fecha: **{fecha_demo}**")
        if st.button("Que 3 trabajadores soliciten este turno"):
            disponibles = sistema.buscar_trabajadores_disponibles(labor_demo, franja_demo, fecha_demo)
            no_disponibles = [t for t in sistema.get_trabajadores() if t not in disponibles]
            candidatos = disponibles[:2] + no_disponibles[:1]
            resultados = []
            for t in candidatos:
                try:
                    sistema.solicitar_asignacion(t, labor_demo, franja_demo, fecha_demo)
                    resultados.append(("ok", f"{t.get_nombre()}: solicitud aceptada, va a la cola."))
                except Exception as e:
                    resultados.append(("error", f"{t.get_nombre()}: rechazado al instante — {e}"))
            st.session_state.demo_resultados = resultados
            st.rerun()
        for tipo, texto in st.session_state.get("demo_resultados", []):
            (st.success if tipo == "ok" else st.error)(texto)
    else:
        st.info("No hay labores cargadas.")

    st.divider()
    st.markdown("### Paso 3 — El sistema procesa la cola y recomienda lo que falta")
    st.caption(f"Solicitudes esperando en la cola ahora mismo: {len(sistema.get_solicitudes_pendientes())}")
    if st.button("Correr el ciclo (procesa pedidos + genera automaticas)"):
        nuevas = sistema.ciclo_semanal(fecha_demo)
        st.success(f"Listo. {len(nuevas)} asignacion(es) Automatica(s) nueva(s) generada(s).")
        st.rerun()

    st.divider()
    st.markdown("### Paso 4 — El supervisor aprueba, rechaza o reasigna")
    pendientes_del_dia = [
        a for a in sistema.obtener_asignaciones()
        if a.get_fecha() == fecha_demo and a.get_estado() != EstadoAsignacion.APROBADA
    ]
    if not pendientes_del_dia:
        st.info("No hay nada pendiente de revisar para esta fecha todavia.")
    for i, a in enumerate(pendientes_del_dia):
        with st.container(border=True):
            st.write(
                f"**{a.get_trabajador().get_nombre()}** -> **{a.get_labor().get_titulo()}** "
                f"en '{a.get_franja().get_nombre()}' — estado: **{a.get_estado()}**"
            )
            b1, b2, b3 = st.columns(3)
            if b1.button("Aprobar", key=f"flujo_aprobar_{i}"):
                supervisor.aprobar_asignacion(a)
                st.rerun()
            if b2.button("Rechazar", key=f"flujo_rechazar_{i}"):
                supervisor.rechazar_asignacion(a, sistema)
                st.rerun()
            otros = [t for t in sistema.get_trabajadores() if t != a.get_trabajador()]
            if otros:
                id_otro = b3.selectbox(
                    "Reasignar a", [t.get_id() for t in otros],
                    format_func=lambda tid: next(t.get_nombre() for t in otros if t.get_id() == tid),
                    key=f"flujo_reasignar_sel_{i}", label_visibility="collapsed",
                )
                if b3.button("Confirmar reasignar", key=f"flujo_reasignar_btn_{i}"):
                    nuevo_t = next(t for t in otros if t.get_id() == id_otro)
                    supervisor.reasignar_asignacion(a, nuevo_t)
                    st.rerun()

    st.divider()
    st.markdown("### Paso 5 — ¿Quedaron todas las labores cubiertas?")
    cobertura = []
    for labor in sistema.get_labores():
        for franja in labor.get_area().get_franjas():
            cubierta = any(
                a.get_labor() == labor and a.get_franja() == franja and a.get_fecha() == fecha_demo
                and a.get_estado() == EstadoAsignacion.APROBADA
                for a in sistema.obtener_asignaciones()
            )
            cobertura.append({
                "Area": labor.get_area().get_nombre(),
                "Labor": labor.get_titulo(),
                "Franja": franja.get_nombre(),
                "Cubierta (Aprobada)": "Si" if cubierta else "No",
            })
    st.dataframe(cobertura, width="stretch", hide_index=True)

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
                "Admin": "Si" if isinstance(trabajador, Supervisor) else "No",
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

    with st.expander("Gestionar habilidades y credenciales de un trabajador"):
        if sistema.get_trabajadores():
            nombres_habilidad_catalogo = sorted(set(
                h.get_habilidad().get_nombre()
                for t in sistema.get_trabajadores()
                for h in t.get_habilidades()
            ))
            nombres_credencial_catalogo = sorted(set(
                c.get_nombre() for t in sistema.get_trabajadores() for c in t.get_credenciales()
            ))

            id_sel = st.selectbox(
                "Trabajador", [t.get_id() for t in sistema.get_trabajadores()],
                format_func=lambda tid: next(t.get_nombre() for t in sistema.get_trabajadores() if t.get_id() == tid),
                key="gestion_trabajador",
            )
            trabajador_sel = next(t for t in sistema.get_trabajadores() if t.get_id() == id_sel)

            st.markdown("**Habilidades actuales**")
            if trabajador_sel.get_habilidades():
                for i, h in enumerate(trabajador_sel.get_habilidades()):
                    hc1, hc2 = st.columns([4, 1])
                    hc1.write(f"{h.get_habilidad().get_nombre()} — {NOMBRES_NIVEL[h.get_nivel()]}")
                    if hc2.button("Quitar", key=f"quitar_hab_{id_sel}_{i}"):
                        restantes = [x for j, x in enumerate(trabajador_sel.get_habilidades()) if j != i]
                        trabajador_sel.set_habilidades(restantes)
                        st.rerun()
            else:
                st.caption("No tiene habilidades cargadas.")

            ah1, ah2, ah3 = st.columns([2, 2, 1])
            habilidad_elegida = ah1.selectbox(
                "Agregar habilidad", ["(nueva)"] + nombres_habilidad_catalogo, key="agregar_habilidad_catalogo"
            )
            habilidad_nueva_texto = ah1.text_input(
                "Nombre si es nueva", key="agregar_habilidad_texto", disabled=habilidad_elegida != "(nueva)"
            )
            nivel_a_agregar = ah2.selectbox(
                "Nivel", [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO],
                format_func=lambda n: NOMBRES_NIVEL[n], key="agregar_habilidad_nivel",
            )
            if ah3.button("Agregar", key="agregar_habilidad_btn"):
                nombre_habilidad = habilidad_nueva_texto.strip() if habilidad_elegida == "(nueva)" else habilidad_elegida
                if nombre_habilidad:
                    nueva_lista = trabajador_sel.get_habilidades() + [
                        HabilidadDeTrabajador(Habilidad(nombre_habilidad), nivel_a_agregar)
                    ]
                    trabajador_sel.set_habilidades(nueva_lista)
                    st.rerun()
                else:
                    st.error("Elegi del catalogo o escribi un nombre nuevo.")

            st.divider()
            st.markdown("**Credenciales actuales**")
            if trabajador_sel.get_credenciales():
                for i, c in enumerate(trabajador_sel.get_credenciales()):
                    vigente = "vigente" if c.esta_activa(date.today()) else "VENCIDA"
                    cc1, cc2 = st.columns([4, 1])
                    cc1.write(f"{c.get_nombre()} — caduca {c.get_fecha_caducidad()} ({vigente})")
                    if cc2.button("Quitar", key=f"quitar_cred_{id_sel}_{i}"):
                        restantes = [x for j, x in enumerate(trabajador_sel.get_credenciales()) if j != i]
                        trabajador_sel.set_credenciales(restantes)
                        st.rerun()
            else:
                st.caption("No tiene credenciales cargadas.")

            ac1, ac2, ac3 = st.columns([2, 2, 1])
            credencial_elegida = ac1.selectbox(
                "Agregar credencial", ["(nueva)"] + nombres_credencial_catalogo, key="agregar_credencial_catalogo"
            )
            credencial_nueva_texto = ac1.text_input(
                "Nombre si es nueva", key="agregar_credencial_texto", disabled=credencial_elegida != "(nueva)"
            )
            dias_vigencia = ac2.number_input(
                "Dias hasta que caduca (negativo = vencida)", value=365, step=30, key="agregar_credencial_dias"
            )
            if ac3.button("Agregar", key="agregar_credencial_btn"):
                nombre_credencial = credencial_nueva_texto.strip() if credencial_elegida == "(nueva)" else credencial_elegida
                if nombre_credencial:
                    nueva_credencial = CredencialProfesional(
                        nombre_credencial,
                        date.today() - timedelta(days=365),
                        date.today() + timedelta(days=int(dias_vigencia)),
                    )
                    trabajador_sel.set_credenciales(trabajador_sel.get_credenciales() + [nueva_credencial])
                    st.rerun()
                else:
                    st.error("Elegi del catalogo o escribi un nombre nuevo.")

    st.divider()
    st.subheader("Registrar nuevo trabajador")
    st.caption(
        "Los atributos adicionales se pasan como **kwargs a `sistema.registrar_personal(...)`."
    )

    col1, col2, col3 = st.columns(3)
    nuevo_id = col1.number_input("ID", min_value=1, step=1, key="nuevo_id")
    nuevo_nombre = col2.text_input("Nombre", key="nuevo_nombre")
    nuevo_horas_max = col3.number_input("Horas maximas semanales", min_value=1, step=1, key="nuevo_horas_max")

    st.caption("Habilidad (opcional)")
    ch1, ch2 = st.columns(2)
    nueva_habilidad_nombre = ch1.text_input("Nombre de la habilidad", key="nueva_habilidad_nombre")
    nueva_habilidad_nivel = ch2.selectbox(
        "Nivel", [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO],
        format_func=lambda n: NOMBRES_NIVEL[n], key="nueva_habilidad_nivel",
    )

    st.caption("Credencial (opcional)")
    cc1, cc2 = st.columns(2)
    nueva_credencial_nombre = cc1.text_input("Nombre de la credencial", key="nueva_credencial_nombre")
    nueva_credencial_dias = cc2.number_input(
        "Dias hasta que caduca (negativo = ya vencida)", value=365, step=30, key="nueva_credencial_dias"
    )

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
            if nueva_habilidad_nombre.strip():
                nuevo.set_habilidades([
                    HabilidadDeTrabajador(Habilidad(nueva_habilidad_nombre.strip()), nueva_habilidad_nivel)
                ])
            if nueva_credencial_nombre.strip():
                nuevo.set_credenciales([
                    CredencialProfesional(
                        nueva_credencial_nombre.strip(),
                        date.today() - timedelta(days=365),
                        date.today() + timedelta(days=int(nueva_credencial_dias)),
                    )
                ])
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

    estados_disponibles = [EstadoAsignacion.AUTOMATICA, EstadoAsignacion.PENDIENTE, EstadoAsignacion.APROBADA]
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

            if asignacion.get_estado() in (EstadoAsignacion.AUTOMATICA, EstadoAsignacion.PENDIENTE):
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
