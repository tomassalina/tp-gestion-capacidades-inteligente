"""Frontend Streamlit para el TP de Gestion de Capacidades Inteligente.

Este modulo NO reimplementa ninguna regla de negocio: todo el trabajo real
(validaciones, asignaciones, aprobaciones, etc.) lo hacen las clases del
directorio padre (Sistema, Supervisor, Trabajador, etc.). Esta app solo arma
la interfaz y llama a los metodos publicos de esas clases.

Navegacion por rol: Trabajador / Supervisor / Sistema, igual que en la vida
real alguien se loguearia con un usuario distinto segun que necesite hacer.
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from datetime import timedelta

from asignacion import Asignacion, AsignacionDuplicadaError, EstadoAsignacion, FranjaSinLugarError, HorasMaximasExcedidasError, TrabajadorNoAptoError
from credencial_profesional import CredencialProfesional
from habilidad import Habilidad, HabilidadDeTrabajador, NivelHabilidad
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador
from seed import armar_seed

NOMBRES_NIVEL = {
    NivelHabilidad.BASICO: "Básico",
    NivelHabilidad.INTERMEDIO: "Intermedio",
    NivelHabilidad.AVANZADO: "Avanzado",
}

st.set_page_config(page_title="Gestión de Capacidades", layout="wide", page_icon="🧩")

if "sistema" not in st.session_state:
    st.session_state.sistema = armar_seed()[0]
sistema: Sistema = st.session_state.sistema


# ---------------------------------------------------------------------------
# Barra superior: titulo + persistencia (siempre visible, no escondida)
# ---------------------------------------------------------------------------
col_titulo, col_guardar, col_cargar, col_reiniciar = st.columns([3, 1, 1, 1])
with col_titulo:
    st.title("🧩 Gestión de Capacidades Inteligente")
    st.caption("Asignación inteligente de personal a labores, por fecha, franja y área")
with col_guardar:
    st.write("")
    if st.button("💾 Guardar todo", width="stretch"):
        sistema.guardar_todo()
        st.toast("Guardado en la carpeta data/", icon="💾")
with col_cargar:
    st.write("")
    if st.button("📂 Cargar guardado", width="stretch"):
        st.session_state.sistema = Sistema.cargar_todo()
        st.toast("Datos recuperados desde data/", icon="📂")
        st.rerun()
with col_reiniciar:
    st.write("")
    if st.button("🔄 Reiniciar demo", width="stretch"):
        st.session_state.sistema = armar_seed()[0]
        st.toast("Demo reiniciada desde cero", icon="🔄")
        st.rerun()

st.divider()


# ---------------------------------------------------------------------------
# Selector de rol: como loguearse con un usuario distinto
# ---------------------------------------------------------------------------
rol = st.radio(
    "Entrar como:",
    ["👷 Trabajador", "🧑‍💼 Supervisor", "⚙️ Sistema (automático)"],
    horizontal=True,
    label_visibility="collapsed",
)

trabajadores_comunes = [t for t in sistema.get_trabajadores() if not isinstance(t, Supervisor)]
supervisores = [t for t in sistema.get_trabajadores() if isinstance(t, Supervisor)]


def tabla(filas):
    st.dataframe(filas, width="stretch", hide_index=True) if filas else st.caption("No hay nada para mostrar todavía.")


def mostrar_error_de_asignacion(error):
    if isinstance(error, TrabajadorNoAptoError):
        partes = []
        if error.habilidades_faltantes:
            partes.append(f"habilidades: {', '.join(sorted(error.habilidades_faltantes))}")
        if error.credenciales_faltantes:
            partes.append(f"credenciales: {', '.join(sorted(error.credenciales_faltantes))}")
        st.error(f"No es apto. Le falta — {' · '.join(partes)}")
    else:
        st.error(str(error))


# ---------------------------------------------------------------------------
# Rol: Trabajador
# ---------------------------------------------------------------------------
if rol == "👷 Trabajador":
    st.caption("Vista de un trabajador: su propio perfil, su agenda, y pedir que lo asignen a una labor.")
    nombre_sel = st.selectbox("¿Quién sos?", [t.get_nombre() for t in trabajadores_comunes], key="trabajador_sel")
    trabajador = next(t for t in trabajadores_comunes if t.get_nombre() == nombre_sel)

    tab_perfil, tab_agenda, tab_solicitar, tab_pendientes = st.tabs(
        ["Mi perfil", "Mi agenda", "Solicitar asignación", "Mis solicitudes pendientes"]
    )

    with tab_perfil:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Habilidades")
            if trabajador.get_habilidades():
                tabla([
                    {"Habilidad": h.get_habilidad().get_nombre(), "Nivel": NOMBRES_NIVEL[h.get_nivel()]}
                    for h in trabajador.get_habilidades()
                ])
            else:
                st.warning("Sin habilidades cargadas todavía — no va a ser apto para ninguna labor que las exija.")
            with st.expander("➕ Agregar habilidad"):
                nombre_hab = st.text_input("Nombre de la habilidad", key=f"nueva_hab_nombre_{trabajador.get_id()}")
                nivel_hab = st.selectbox(
                    "Nivel", [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO],
                    format_func=lambda n: NOMBRES_NIVEL[n], key=f"nueva_hab_nivel_{trabajador.get_id()}",
                )
                if st.button("Agregar", key=f"agregar_hab_{trabajador.get_id()}") and nombre_hab.strip():
                    trabajador.agregar_habilidad(HabilidadDeTrabajador(Habilidad(nombre_hab.strip()), nivel_hab))
                    st.rerun()
        with c2:
            st.subheader("Credenciales")
            tabla([
                {
                    "Credencial": c.get_nombre(),
                    "Caduca": c.get_fecha_caducidad(),
                    "Estado": "✅ Vigente" if c.esta_activa(date.today()) else "⛔ Vencida",
                }
                for c in trabajador.get_credenciales()
            ])
            with st.expander("➕ Agregar credencial"):
                nombre_cred = st.text_input("Nombre de la credencial", key=f"nueva_cred_nombre_{trabajador.get_id()}")
                dias_vigencia = st.number_input(
                    "Días hasta que caduca (negativo = ya vencida)", value=365, step=30, key=f"nueva_cred_dias_{trabajador.get_id()}"
                )
                if st.button("Agregar", key=f"agregar_cred_{trabajador.get_id()}") and nombre_cred.strip():
                    nueva_credencial = CredencialProfesional(
                        nombre_cred.strip(), date.today() - timedelta(days=365), date.today() + timedelta(days=int(dias_vigencia))
                    )
                    trabajador.set_credenciales(trabajador.get_credenciales() + [nueva_credencial])
                    st.rerun()

        st.subheader("Horas esta semana")
        maximas = trabajador.get_horas_maximas_semana()
        asignadas = trabajador.get_horas_asignadas()
        st.progress(min(asignadas / maximas, 1.0), text=f"{asignadas} / {maximas} hs")

        st.subheader("Atributos opcionales (**kwargs)")
        atributos = trabajador.get_atributos()
        st.write(", ".join(f"**{k}**: {v}" for k, v in atributos.items()) or "Sin atributos opcionales.")

        st.subheader("Comparar con otro trabajador")
        otro_nombre = st.selectbox(
            "Comparar con", [t.get_nombre() for t in trabajadores_comunes if t != trabajador], key="comparar_con"
        )
        if otro_nombre:
            otro = next(t for t in trabajadores_comunes if t.get_nombre() == otro_nombre)
            c1, c2 = st.columns(2)
            c1.metric("Habilidades en común", len(trabajador.habilidades_en_comun(otro)))
            c2.metric("Habilidades exclusivas suyas", len(trabajador.habilidades_exclusivas(otro)))

    with tab_agenda:
        st.caption("Lista enlazada (`Agenda`), siempre ordenada por fecha y franja — regla 17.")
        agenda = trabajador.get_agenda().recorrer()
        tabla([
            {
                "Fecha": a.get_fecha(), "Franja": a.get_franja().get_nombre(),
                "Labor": a.get_labor().get_titulo(), "Estado": a.get_estado(),
            }
            for a in agenda
        ])

    with tab_solicitar:
        labores = sistema.get_labores()
        id_labor = st.selectbox(
            "Labor", [l.get_id() for l in labores],
            format_func=lambda lid: next(l.get_titulo() for l in labores if l.get_id() == lid),
            key="sol_labor",
        )
        labor = next(l for l in labores if l.get_id() == id_labor)
        franja = st.selectbox(
            "Franja", labor.get_area().get_franjas(), format_func=lambda f: f.get_nombre(), key="sol_franja"
        )
        fecha = st.date_input("Fecha", value=date.today(), key="sol_fecha")
        if st.button("Solicitar asignación", type="primary"):
            try:
                trabajador.solicitar_asignacion(sistema, labor, franja, fecha)
                st.success("Solicitud enviada — queda esperando en la cola hasta que se procese.")
            except (TrabajadorNoAptoError, AsignacionDuplicadaError, HorasMaximasExcedidasError, FranjaSinLugarError) as e:
                mostrar_error_de_asignacion(e)
            except Exception as e:
                st.error(f"Error inesperado: {e}")

    with tab_pendientes:
        propias = [
            s for s in sistema.get_solicitudes_pendientes().recorrer() if s[0] == trabajador
        ]
        tabla([
            {"Labor": labor.get_titulo(), "Franja": franja.get_nombre(), "Fecha": fecha}
            for (_, labor, franja, fecha) in propias
        ])


# ---------------------------------------------------------------------------
# Rol: Supervisor
# ---------------------------------------------------------------------------
elif rol == "🧑‍💼 Supervisor":
    st.caption("Vista de un supervisor: ver disponibilidad, aprobar/rechazar/reasignar, asignar directo, y auditoría.")
    nombre_sel = st.selectbox("¿Quién sos?", [s.get_nombre() for s in supervisores], key="supervisor_sel")
    supervisor = next(s for s in supervisores if s.get_nombre() == nombre_sel)

    tab_disp, tab_cola, tab_directo, tab_reglas, tab_registrar, tab_catalogo, tab_bitacora, tab_ocupacion = st.tabs(
        ["Disponibilidad", "Cola y pendientes", "Asignar directo", "Reglas del área",
         "Registrar personal", "Catálogo", "Bitácora", "Ocupación"]
    )

    with tab_disp:
        labores = sistema.get_labores()
        id_labor = st.selectbox(
            "Labor", [l.get_id() for l in labores],
            format_func=lambda lid: next(l.get_titulo() for l in labores if l.get_id() == lid),
            key="disp_labor",
        )
        labor = next(l for l in labores if l.get_id() == id_labor)
        franja = st.selectbox("Franja", labor.get_area().get_franjas(), format_func=lambda f: f.get_nombre(), key="disp_franja")
        fecha = st.date_input("Fecha", value=date.today(), key="disp_fecha")

        disponibles = sistema.buscar_trabajadores_disponibles(labor, franja, fecha)
        st.subheader(f"Disponibles ({len(disponibles)})")
        tabla([{"Nombre": t.get_nombre(), "Rol": t.get_atributo("rol", "-")} for t in disponibles])

        st.subheader("¿Por qué alguien no está disponible?")
        no_disponibles = [t for t in trabajadores_comunes if t not in disponibles]
        if no_disponibles:
            nombre_chequear = st.selectbox(
                "Trabajador", [t.get_nombre() for t in no_disponibles], key="disp_chequear"
            )
            trabajador_chequear = next(t for t in no_disponibles if t.get_nombre() == nombre_chequear)
            try:
                Asignacion.evaluar_aptitud(trabajador_chequear, labor, fecha)
                st.info("Es apto en habilidades/credenciales/horas — no aparece disponible por capacidad de la franja o exclusividad de la labor (regla 6 o 7).")
            except TrabajadorNoAptoError as e:
                mostrar_error_de_asignacion(e)
            except (HorasMaximasExcedidasError,) as e:
                st.error(str(e))
        else:
            st.caption("Todos los trabajadores están disponibles para esta combinación.")

    with tab_cola:
        st.subheader("Cola de solicitudes (FIFO)")
        cola = sistema.get_solicitudes_pendientes().recorrer()
        tabla([
            {"Trabajador": t.get_nombre(), "Labor": labor.get_titulo(), "Franja": franja.get_nombre(), "Fecha": fecha}
            for (t, labor, franja, fecha) in cola
        ])
        if st.button("▶️ Procesar cola ahora"):
            sistema.procesar_solicitudes_pendientes()
            st.rerun()

        st.divider()
        st.subheader("Asignaciones sin resolver (Pendiente / Automática)")
        sin_resolver = [a for a in sistema.obtener_asignaciones() if a.get_estado() != EstadoAsignacion.APROBADA]
        for i, a in enumerate(sin_resolver):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
            c1.write(f"**{a.get_trabajador().get_nombre()}** → {a.get_labor().get_titulo()} ({a.get_franja().get_nombre()}, {a.get_fecha()}) — *{a.get_estado()}*")
            if c2.button("Aprobar", key=f"aprobar_{i}"):
                supervisor.aprobar_asignacion(sistema, a)
                st.rerun()
            if c3.button("Rechazar", key=f"rechazar_{i}"):
                supervisor.rechazar_asignacion(sistema, a)
                st.rerun()
            otros = [t for t in trabajadores_comunes if t != a.get_trabajador()]
            nuevo_nombre = c4.selectbox("Reasignar a", [t.get_nombre() for t in otros], key=f"reasignar_{i}", label_visibility="collapsed")
            if c4.button("Confirmar reasignación", key=f"confirmar_reasignar_{i}"):
                try:
                    supervisor.reasignar_asignacion(a, next(t for t in otros if t.get_nombre() == nuevo_nombre))
                    st.rerun()
                except (TrabajadorNoAptoError, HorasMaximasExcedidasError) as e:
                    mostrar_error_de_asignacion(e)
                except Exception as e:
                    st.error(f"Error inesperado: {e}")
        if not sin_resolver:
            st.caption("No hay asignaciones pendientes ni automáticas en este momento.")

    with tab_directo:
        id_labor = st.selectbox(
            "Labor", [l.get_id() for l in sistema.get_labores()],
            format_func=lambda lid: next(l.get_titulo() for l in sistema.get_labores() if l.get_id() == lid),
            key="directo_labor",
        )
        labor = next(l for l in sistema.get_labores() if l.get_id() == id_labor)
        franja = st.selectbox("Franja", labor.get_area().get_franjas(), format_func=lambda f: f.get_nombre(), key="directo_franja")
        fecha = st.date_input("Fecha", value=date.today(), key="directo_fecha")
        trabajador_nombre = st.selectbox("Trabajador", [t.get_nombre() for t in trabajadores_comunes], key="directo_trabajador")
        if st.button("Asignar directo", type="primary"):
            trabajador = next(t for t in trabajadores_comunes if t.get_nombre() == trabajador_nombre)
            try:
                supervisor.asignar_trabajador(sistema, trabajador, labor, franja, fecha)
                st.success(f"{trabajador.get_nombre()} asignado directamente, ya Aprobado.")
            except (TrabajadorNoAptoError, AsignacionDuplicadaError, HorasMaximasExcedidasError, FranjaSinLugarError) as e:
                mostrar_error_de_asignacion(e)
            except Exception as e:
                st.error(f"Error inesperado: {e}")

    with tab_reglas:
        area_sel = st.selectbox("Área", [a.get_nombre() for a in sistema.get_areas()], key="reglas_area")
        area = next(a for a in sistema.get_areas() if a.get_nombre() == area_sel)
        st.write("**Credenciales obligatorias actuales:**", ", ".join(area.get_credenciales_obligatorias()) or "-")
        nueva = st.text_input("Nueva credencial obligatoria", key="reglas_nueva")
        if st.button("Agregar regla") and nueva.strip():
            supervisor.agregar_regla_area(area, nueva.strip())
            st.rerun()

    with tab_registrar:
        st.caption("Alta de personal nuevo con atributos opcionales (**kwargs) — extensión de consigna.")
        nuevo_id = st.number_input("Legajo (ID)", min_value=100, step=1, value=100, key="registrar_id")
        nuevo_nombre = st.text_input("Nombre", key="registrar_nombre")
        nuevas_horas = st.number_input("Horas máximas semana", min_value=1, value=20, key="registrar_horas")
        col_rol, col_area = st.columns(2)
        rol_attr = col_rol.text_input("Rol (opcional)", key="registrar_rol")
        area_attr = col_area.selectbox("Área de equipo (opcional)", ["(sin asignar)"] + [a.get_nombre() for a in sistema.get_areas()], key="registrar_area")
        if st.button("Registrar", type="primary") and nuevo_nombre.strip():
            atributos = {}
            if rol_attr.strip():
                atributos["rol"] = rol_attr.strip()
            if area_attr != "(sin asignar)":
                atributos["area_equipo"] = area_attr
            try:
                nuevo = sistema.registrar_personal(int(nuevo_id), nuevo_nombre.strip(), int(nuevas_horas), **atributos)
                st.success(f"{nuevo.get_nombre()} registrado (legajo {nuevo.get_id()}).")
            except Exception as e:
                st.error(f"No se pudo registrar: {e}")

    with tab_catalogo:
        st.caption("Áreas, franjas y labores existentes — reglas 3, 6 y 10.")
        for area in sistema.get_areas():
            with st.expander(area.get_nombre()):
                st.write("**Credenciales obligatorias:**", ", ".join(area.get_credenciales_obligatorias()) or "-")
                tabla([{"Franja": f.get_nombre(), "Capacidad": f.get_capacidad()} for f in area.get_franjas()])
        st.subheader("Labores")
        tabla([
            {
                "Labor": l.get_titulo(), "Área": l.get_area().get_nombre(), "Duración (hs)": l.get_duracion_horas(),
                "Habilidades requeridas": ", ".join(
                    f"{h.get_habilidad().get_nombre()} ({NOMBRES_NIVEL[h.get_nivel_minimo()]})"
                    for h in l.get_habilidades_requeridas()
                ),
            }
            for l in sistema.get_labores()
        ])

    with tab_bitacora:
        st.caption("Registro inmutable de toda propuesta, aprobación y reversión — regla 18.")
        registros = sorted(sistema.obtener_bitacora(), key=lambda r: r[0], reverse=True)
        tabla([
            {"Fecha y hora": r[0], "Acción": r[1], "Labor": r[2].get_titulo(), "Trabajador": r[3].get_nombre()}
            for r in registros
        ])

    with tab_ocupacion:
        st.caption("Consulta inmediata por fecha+franja+área, sin recorrer asignaciones — regla 16.")
        area_sel = st.selectbox("Área", [a.get_nombre() for a in sistema.get_areas()], key="ocup_area")
        area = next(a for a in sistema.get_areas() if a.get_nombre() == area_sel)
        franja = st.selectbox("Franja", area.get_franjas(), format_func=lambda f: f.get_nombre(), key="ocup_franja")
        fecha = st.date_input("Fecha", value=date.today(), key="ocup_fecha")
        ocupados = sistema.contar_ocupacion(fecha, franja, area)
        st.metric("Ocupación", f"{ocupados} / {franja.get_capacidad()}")


# ---------------------------------------------------------------------------
# Rol: Sistema (simula lo que en la vida real correria un cron de noche)
# ---------------------------------------------------------------------------
else:
    st.caption("Vista del sistema automático: lo que en la vida real correría solo, de noche, sin que nadie lo dispare a mano.")
    st.info("No hay cron real posible en una demo: este rol simula lo que el sistema haría automáticamente al cierre de cada semana.")
    fecha = st.date_input("Fecha para el nuevo ciclo", value=date.today(), key="sistema_fecha")

    antes = len(sistema.obtener_asignaciones())
    if st.button("▶️ Ejecutar ciclo semanal completo", type="primary", width="stretch"):
        nuevas = sistema.ciclo_semanal(fecha)
        st.success(
            f"Ciclo ejecutado: horas reiniciadas (regla 12), cola procesada, y se generaron {len(nuevas)} sugerencias automáticas (regla 11)."
        )
        tabla([
            {
                "Trabajador": s.get_trabajador().get_nombre(), "Labor": s.get_labor().get_titulo(),
                "Franja": s.get_franja().get_nombre(), "Estado": s.get_estado(),
            }
            for s in nuevas
        ])

    st.divider()
    st.subheader("Estado actual del sistema")
    c1, c2, c3 = st.columns(3)
    c1.metric("Trabajadores", len(trabajadores_comunes))
    c2.metric("Asignaciones activas", len(sistema.obtener_asignaciones()))
    c3.metric("Solicitudes en cola", sistema.get_solicitudes_pendientes().get_cantidad())
