"""
Analisis con NumPy y Matplotlib sobre el dataset generado por generar_dataset.py.

Tres ejercicios:
  1. Carga laboral (horas asignadas vs horas maximas semanales, por trabajador y categoria)
  2. Cumplimiento de credenciales (activas vs vencidas, causas de rechazo de asignaciones)
  3. Capacidad de areas y franjas horarias (ocupacion real vs capacidad, heatmap)

Corre: python analisis/analisis_capacidades.py
Lee CSVs de analisis/data/, escribe PNGs en analisis/graficos/
y un resumen de metricas en analisis/resumen_metricas.json (insumo para el PPTX).
"""
import csv
import json
import os
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DIRECTORIO_ANALISIS = os.path.dirname(os.path.abspath(__file__))
RAIZ_REPO = os.path.dirname(DIRECTORIO_ANALISIS)
sys.path.insert(0, RAIZ_REPO)

from repositorio_csv import decodificar_lista  # noqa: E402
from credencial_profesional import CredencialProfesional  # noqa: E402
from franja import Franja, TipoFranja  # noqa: E402
from trabajador import Trabajador  # noqa: E402

DIRECTORIO_DATOS = os.path.join(DIRECTORIO_ANALISIS, "data")
DIRECTORIO_GRAFICOS = os.path.join(DIRECTORIO_ANALISIS, "graficos")
ORDEN_CATEGORIAS = ["Tecnico", "Senior", "Especialista", "Supervisor"]
ORDEN_FRANJAS = [TipoFranja.MANIANA, TipoFranja.TARDE, TipoFranja.NOCHE]


def leer_csv(nombre_archivo):
    ruta = os.path.join(DIRECTORIO_DATOS, nombre_archivo)
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def leer_trabajadores():
    filas = leer_csv("trabajadores.csv") + leer_csv("supervisores.csv")
    trabajadores = {}
    for fila in filas:
        atributos = Trabajador.atributos_desde_texto(fila["atributos"])
        credenciales = decodificar_lista(fila["credenciales"], CredencialProfesional.desde_texto)
        trabajadores[int(fila["id"])] = {
            "nombre": fila["nombre"],
            "categoria": atributos.get("categoria", "Sin categoria"),
            "horas_maximas_semana": float(fila["horas_maximas_semana"]),
            "credenciales": credenciales,
        }
    return trabajadores


def leer_labores():
    filas = leer_csv("labores.csv")
    return {
        int(fila["id"]): {"duracion_horas": float(fila["duracion_horas"]), "area": fila["area"]}
        for fila in filas
    }


def leer_areas():
    filas = leer_csv("areas.csv")
    areas = {}
    for fila in filas:
        franjas = decodificar_lista(fila["franjas"], Franja.desde_texto)
        areas[fila["nombre"]] = {franja.get_nombre(): franja.get_capacidad() for franja in franjas}
    return areas


def leer_asignaciones():
    return leer_csv("asignaciones.csv")


def leer_conflictos():
    return leer_csv("conflictos.csv")


def guardar_grafico(fig, nombre_archivo):
    os.makedirs(DIRECTORIO_GRAFICOS, exist_ok=True)
    ruta = os.path.join(DIRECTORIO_GRAFICOS, nombre_archivo)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


# ---------------------------------------------------------------------------
# Ejercicio 1: carga laboral
# ---------------------------------------------------------------------------

def analizar_carga_laboral(trabajadores, labores, asignaciones):
    # horas_maximas_semana es un tope SEMANAL (se resetea cada semana, regla 12 del core).
    # Sumar las horas de las ~1000 asignaciones de TODO el periodo (90 dias) y dividirlas
    # por un tope de UNA sola semana da utilizaciones de cientos de % sin sentido: hay que
    # repartir cada asignacion en la semana en la que ocurrio y comparar semana contra semana.
    fechas = [date.fromisoformat(a["fecha"]) for a in asignaciones]
    fecha_min = min(fechas)
    n_semanas = max(1, (max(fechas) - fecha_min).days // 7 + 1)

    ids = list(trabajadores.keys())
    indice_por_id = {id_t: i for i, id_t in enumerate(ids)}
    categorias = np.array([trabajadores[id_t]["categoria"] for id_t in ids])
    maximas = np.array([trabajadores[id_t]["horas_maximas_semana"] for id_t in ids])

    horas_matriz = np.zeros((len(ids), n_semanas))
    for asignacion, fecha in zip(asignaciones, fechas):
        id_t = int(asignacion["trabajador_id"])
        semana = (fecha - fecha_min).days // 7
        duracion = labores[int(asignacion["labor_id"])]["duracion_horas"]
        horas_matriz[indice_por_id[id_t], semana] += duracion

    utilizacion_semanal = horas_matriz / maximas[:, None] * 100  # (trabajadores x semanas)
    utilizacion = utilizacion_semanal.mean(axis=1)  # promedio semanal por trabajador, en [0, 100]

    sin_asignaciones = [trabajadores[id_t]["nombre"] for id_t in ids if horas_matriz[indice_por_id[id_t]].sum() == 0]
    alta_utilizacion = [
        (trabajadores[id_t]["nombre"], round(util, 1))
        for id_t, util in zip(ids, utilizacion) if util >= 80
    ]
    subutilizados_pct = float(np.mean(utilizacion < 30) * 100)
    sin_asignaciones_pct = len(sin_asignaciones) / len(ids) * 100

    print("=== Ejercicio 1: Carga laboral ===")
    print(f"Periodo simulado: {n_semanas} semanas")
    print(f"Utilizacion semanal promedio: {utilizacion.mean():.1f}% | mediana: {np.median(utilizacion):.1f}% | desvio: {utilizacion.std():.1f}")
    print(f"Trabajadores sin ninguna asignacion en todo el periodo: {len(sin_asignaciones)} de {len(ids)} ({sin_asignaciones_pct:.1f}%)")
    print(f"Trabajadores con uso sostenido alto (>=80% promedio semanal): {len(alta_utilizacion)}")
    print(f"Trabajadores subutilizados (<30% promedio semanal): {subutilizados_pct:.1f}%")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(utilizacion, bins=20, color="#4C72B0", edgecolor="white")
    ax.axvline(80, color="#C44E52", linestyle="--", linewidth=1.5, label="Uso sostenido alto (80%)")
    ax.set_title("Distribucion de utilizacion semanal promedio por trabajador")
    ax.set_xlabel(f"% de utilizacion semanal promedio en {n_semanas} semanas (horas/semana / horas maximas)")
    ax.set_ylabel("Cantidad de trabajadores")
    ax.set_xlim(0, 100)
    ax.legend()
    ruta_hist = guardar_grafico(fig, "01_histograma_utilizacion.png")

    datos_boxplot = [utilizacion[categorias == categoria] for categoria in ORDEN_CATEGORIAS]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.boxplot(datos_boxplot, tick_labels=ORDEN_CATEGORIAS, showmeans=True)
    ax.axhline(80, color="#C44E52", linestyle="--", linewidth=1, label="Uso sostenido alto (80%)")
    ax.set_title("Utilizacion semanal promedio por categoria de trabajador")
    ax.set_ylabel("% de utilizacion semanal promedio")
    ax.set_ylim(0, 100)
    ax.legend()
    ruta_boxplot = guardar_grafico(fig, "02_boxplot_categoria.png")

    return {
        "n_semanas_simuladas": n_semanas,
        "utilizacion_promedio": round(float(utilizacion.mean()), 1),
        "utilizacion_mediana": round(float(np.median(utilizacion)), 1),
        "utilizacion_desvio": round(float(utilizacion.std()), 1),
        "cantidad_sin_asignaciones": len(sin_asignaciones),
        "porcentaje_sin_asignaciones": round(sin_asignaciones_pct, 1),
        "cantidad_alta_utilizacion": len(alta_utilizacion),
        "top_alta_utilizacion": sorted(alta_utilizacion, key=lambda par: -par[1])[:5],
        "porcentaje_subutilizados": round(subutilizados_pct, 1),
        "graficos": [ruta_hist, ruta_boxplot],
    }


# ---------------------------------------------------------------------------
# Ejercicio 2: cumplimiento de credenciales
# ---------------------------------------------------------------------------

def analizar_credenciales(trabajadores, conflictos, asignaciones):
    hoy = date.today()
    nombres_credenciales = []
    activas = 0
    vencidas = 0
    for datos in trabajadores.values():
        for credencial in datos["credenciales"]:
            nombres_credenciales.append(credencial.get_nombre())
            if credencial.esta_activa(hoy):
                activas += 1
            else:
                vencidas += 1

    nombres_arr = np.array(nombres_credenciales)
    nombres_unicos, conteos = np.unique(nombres_arr, return_counts=True)
    orden = np.argsort(-conteos)
    ranking_credenciales = list(zip(nombres_unicos[orden].tolist(), conteos[orden].tolist()))

    conflictos_credencial = [c for c in conflictos if c["tipo_conflicto"] == "CREDENCIAL_VENCIDA"]
    total_intentos = len(asignaciones) + len(conflictos)
    porcentaje_rechazo_credencial = len(conflictos_credencial) / total_intentos * 100 if total_intentos else 0

    tipos_conflicto, conteos_conflicto = np.unique(
        np.array([c["tipo_conflicto"] for c in conflictos]), return_counts=True
    )

    print("\n=== Ejercicio 2: Cumplimiento de credenciales ===")
    total_credenciales = activas + vencidas
    print(f"Credenciales activas: {activas} ({activas/total_credenciales*100:.1f}%) | vencidas: {vencidas} ({vencidas/total_credenciales*100:.1f}%)")
    print(f"Asignaciones rechazadas por credencial vencida: {len(conflictos_credencial)} ({porcentaje_rechazo_credencial:.1f}% de los intentos)")
    print(f"Credencial mas demandada: {ranking_credenciales[0][0]} ({ranking_credenciales[0][1]} veces)")

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.bar(["Activas", "Vencidas"], [activas, vencidas], color=["#55A868", "#C44E52"])
    ax.set_title("Credenciales del personal: activas vs. vencidas")
    ax.set_ylabel("Cantidad de credenciales")
    for i, valor in enumerate([activas, vencidas]):
        ax.text(i, valor, str(valor), ha="center", va="bottom")
    ruta_barras = guardar_grafico(fig, "03_barras_credenciales.png")

    orden_desc = np.argsort(conteos_conflicto)  # barh dibuja de abajo hacia arriba
    tipos_ordenados = tipos_conflicto[orden_desc]
    conteos_ordenados = conteos_conflicto[orden_desc]
    porcentajes_ordenados = conteos_ordenados / conteos_ordenados.sum() * 100

    fig, ax = plt.subplots(figsize=(7, 4.5))
    barras = ax.barh(tipos_ordenados, conteos_ordenados, color="#C44E52")
    for barra, cantidad, porcentaje in zip(barras, conteos_ordenados, porcentajes_ordenados):
        ax.text(
            barra.get_width() + max(conteos_ordenados) * 0.01, barra.get_y() + barra.get_height() / 2,
            f"{cantidad} ({porcentaje:.1f}%)", va="center", fontsize=10,
        )
    ax.set_title("Causas de rechazo de asignaciones")
    ax.set_xlabel("Cantidad de conflictos")
    ax.set_xlim(0, max(conteos_ordenados) * 1.22)
    ruta_causas = guardar_grafico(fig, "04_barras_causas_rechazo.png")

    return {
        "credenciales_activas": activas,
        "credenciales_vencidas": vencidas,
        "porcentaje_activas": round(activas / total_credenciales * 100, 1),
        "porcentaje_rechazo_por_credencial": round(porcentaje_rechazo_credencial, 1),
        "ranking_credenciales": ranking_credenciales,
        "graficos": [ruta_barras, ruta_causas],
    }


# ---------------------------------------------------------------------------
# Ejercicio 3: capacidad de areas y franjas horarias
# ---------------------------------------------------------------------------

def analizar_franjas_areas(areas, labores, asignaciones, conflictos):
    # La capacidad de una Franja es un tope POR DIA (Asignacion.contar_ocupantes filtra
    # tambien por fecha). Para comparar con la ocupacion acumulada de todo el periodo
    # simulado hay que escalar la capacidad por la cantidad de dias distintos del dataset,
    # si no, sumar ~90 dias de ocupacion contra una capacidad de un solo dia da >100% siempre.
    nombres_areas = list(areas.keys())
    n_dias_unicos = max(1, len({asignacion["fecha"] for asignacion in asignaciones}))

    ocupacion = np.zeros((len(nombres_areas), len(ORDEN_FRANJAS)))
    capacidad_diaria = np.zeros((len(nombres_areas), len(ORDEN_FRANJAS)))
    for i, area in enumerate(nombres_areas):
        for j, franja in enumerate(ORDEN_FRANJAS):
            capacidad_diaria[i, j] = areas[area].get(franja, 0)
    capacidad_periodo = capacidad_diaria * n_dias_unicos

    for asignacion in asignaciones:
        area = labores[int(asignacion["labor_id"])]["area"]
        franja = asignacion["franja"]
        if area in nombres_areas and franja in ORDEN_FRANJAS:
            i = nombres_areas.index(area)
            j = ORDEN_FRANJAS.index(franja)
            ocupacion[i, j] += 1

    with np.errstate(divide="ignore", invalid="ignore"):
        porcentaje_ocupacion = np.where(capacidad_periodo > 0, ocupacion / capacidad_periodo * 100, 0)

    conflictos_franja = [c for c in conflictos if c["tipo_conflicto"] == "FRANJA_COMPLETA"]
    rechazos_por_area = {}
    for conflicto in conflictos_franja:
        rechazos_por_area[conflicto["area"]] = rechazos_por_area.get(conflicto["area"], 0) + 1

    i_max, j_max = np.unravel_index(np.argmax(porcentaje_ocupacion), porcentaje_ocupacion.shape)

    print("\n=== Ejercicio 3: Capacidad de areas y franjas horarias ===")
    print(f"Ocupacion promedio: {porcentaje_ocupacion.mean():.1f}%")
    print(f"Combinacion mas saturada: {nombres_areas[i_max]} / {ORDEN_FRANJAS[j_max]} ({porcentaje_ocupacion[i_max, j_max]:.1f}%)")
    print(f"Rechazos por franja completa: {len(conflictos_franja)}")

    fig, ax = plt.subplots(figsize=(7, 5.5))
    imagen = ax.imshow(porcentaje_ocupacion, cmap="YlOrRd", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(ORDEN_FRANJAS)))
    ax.set_xticklabels(ORDEN_FRANJAS)
    ax.set_yticks(range(len(nombres_areas)))
    ax.set_yticklabels(nombres_areas)
    for i in range(len(nombres_areas)):
        for j in range(len(ORDEN_FRANJAS)):
            ax.text(j, i, f"{porcentaje_ocupacion[i, j]:.0f}%", ha="center", va="center", color="black")
    fig.colorbar(imagen, ax=ax, label="% de ocupacion")
    ax.set_title("Ocupacion real vs. capacidad: Area x Franja")
    ruta_heatmap = guardar_grafico(fig, "05_heatmap_area_franja.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    areas_con_rechazo = list(rechazos_por_area.keys()) or ["(sin rechazos)"]
    valores_rechazo = [rechazos_por_area.get(a, 0) for a in areas_con_rechazo]
    ax.bar(areas_con_rechazo, valores_rechazo, color="#C44E52")
    ax.set_title("Rechazos de asignacion por franja completa, segun area")
    ax.set_ylabel("Cantidad de rechazos")
    ax.tick_params(axis="x", rotation=30)
    ruta_barras = guardar_grafico(fig, "06_barras_rechazos_franja.png")

    return {
        "ocupacion_promedio": round(float(porcentaje_ocupacion.mean()), 1),
        "combinacion_mas_saturada": f"{nombres_areas[i_max]} / {ORDEN_FRANJAS[j_max]}",
        "ocupacion_mas_saturada": round(float(porcentaje_ocupacion[i_max, j_max]), 1),
        "rechazos_por_franja_completa": len(conflictos_franja),
        "graficos": [ruta_heatmap, ruta_barras],
    }


def main():
    trabajadores = leer_trabajadores()
    labores = leer_labores()
    areas = leer_areas()
    asignaciones = leer_asignaciones()
    conflictos = leer_conflictos()

    resumen = {
        "dataset": {
            "trabajadores": len(trabajadores),
            "labores": len(labores),
            "areas": len(areas),
            "asignaciones": len(asignaciones),
            "conflictos": len(conflictos),
        },
        "carga_laboral": analizar_carga_laboral(trabajadores, labores, asignaciones),
        "credenciales": analizar_credenciales(trabajadores, conflictos, asignaciones),
        "franjas_areas": analizar_franjas_areas(areas, labores, asignaciones, conflictos),
    }

    ruta_resumen = os.path.join(DIRECTORIO_ANALISIS, "resumen_metricas.json")
    with open(ruta_resumen, "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2)

    print(f"\nGraficos guardados en: {DIRECTORIO_GRAFICOS}")
    print(f"Resumen de metricas guardado en: {ruta_resumen}")


if __name__ == "__main__":
    main()
