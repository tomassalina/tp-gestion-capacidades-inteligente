"""
Genera un dataset sintetico grande para el analisis con NumPy/Matplotlib,
usando las clases reales del sistema (no datos sueltos) para que todo
respete las mismas reglas de negocio que ya estan implementadas en el core.

Corre: python analisis/generar_dataset.py
Escribe CSVs en analisis/data/ (los oficiales via Sistema.guardar_todo
mas un conflictos.csv propio con los rechazos de asignacion).
"""
import csv
import io
import os
import random
import sys
from contextlib import redirect_stdout
from datetime import date, timedelta

DIRECTORIO_ANALISIS = os.path.dirname(os.path.abspath(__file__))
RAIZ_REPO = os.path.dirname(DIRECTORIO_ANALISIS)
sys.path.insert(0, RAIZ_REPO)

from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida  # noqa: E402
from credencial_profesional import CredencialProfesional  # noqa: E402
from franja import Franja, TipoFranja  # noqa: E402
from area_de_trabajo import AreaDeTrabajo  # noqa: E402
from labor import Labor  # noqa: E402
from trabajador import Trabajador  # noqa: E402
from supervisor import Supervisor  # noqa: E402
from sistema import Sistema  # noqa: E402
from asignacion import (  # noqa: E402
    Asignacion,
    EstadoAsignacion,
    TrabajadorNoAptoError,
    HorasMaximasExcedidasError,
    FranjaSinLugarError,
    AsignacionDuplicadaError,
)
from tipo_accion_bitacora import TipoAccionBitacora  # noqa: E402

random.seed(42)

DIRECTORIO_DATOS = os.path.join(DIRECTORIO_ANALISIS, "data")

NOMBRES_HABILIDADES = [
    "Soldadura", "Programacion PLC", "Manejo de Robots", "Redes Industriales",
    "Quimica Analitica", "Electricidad Industrial", "Manejo de Grua",
    "Calibracion de Equipos", "Seguridad en Alturas", "Logistica de Almacen",
    "Mecanizado CNC", "Supervision de Planta",
]

NOMBRES_CREDENCIALES = [
    "Seguridad Electrica Nivel 3", "Trabajo en Altura", "CCNA",
    "Sustancias Peligrosas", "Operador de Robots", "Redes Industriales",
]

NOMBRES_AREAS = [
    "Planta Robotica", "Centro de Datos", "Alta Tension",
    "Laboratorio Industrial", "Centro Logistico", "Planta Quimica",
]

PROPORCION_CATEGORIAS = {"Tecnico": 0.60, "Senior": 0.20, "Especialista": 0.15, "Supervisor": 0.05}
HORAS_MAXIMAS_POR_CATEGORIA = {
    "Tecnico": 40, "Senior": 44, "Especialista": 40, "Supervisor": 35,
}

N_TRABAJADORES = 200
N_LABORES = 150
ASIGNACIONES_OBJETIVO = 1000
DIAS_HISTORIA = 90
INTENTOS_MAXIMOS = 6000
PROBABILIDAD_REUTILIZAR_SLOT = 0.08
PROBABILIDAD_INTENTO_SIN_FILTRAR = 0.14


def construir_habilidades():
    return {nombre: Habilidad(nombre) for nombre in NOMBRES_HABILIDADES}


def construir_areas():
    areas = []
    for nombre in NOMBRES_AREAS:
        franjas = [
            Franja(tipo_franja, random.randint(3, 10))
            for tipo_franja in (TipoFranja.MANIANA, TipoFranja.TARDE, TipoFranja.NOCHE)
        ]
        n_credenciales = random.randint(0, 2)
        credenciales_obligatorias = random.sample(NOMBRES_CREDENCIALES, n_credenciales)
        areas.append(AreaDeTrabajo(nombre, credenciales_obligatorias, franjas))
    return areas


def construir_labores(areas, habilidades_por_nombre):
    labores = []
    for id_labor in range(1, N_LABORES + 1):
        area = random.choice(areas)
        n_habilidades = random.randint(1, 3)
        nombres_habilidades = random.sample(NOMBRES_HABILIDADES, n_habilidades)
        habilidades_requeridas = [
            HabilidadRequerida(habilidades_por_nombre[nombre], random.choice(
                [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO]
            ))
            for nombre in nombres_habilidades
        ]
        n_credenciales = random.randint(0, 2)
        credenciales_requeridas = random.sample(NOMBRES_CREDENCIALES, n_credenciales)
        duracion_horas = round(random.uniform(1, 8), 1)
        labores.append(Labor(
            id_labor,
            titulo=f"{area.get_nombre()} - Tarea {id_labor}",
            descripcion=f"Labor operativa #{id_labor} del area {area.get_nombre()}",
            duracion_horas=duracion_horas,
            habilidades_requeridas=habilidades_requeridas,
            credenciales_requeridas=credenciales_requeridas,
            area=area,
        ))
    return labores


def generar_credencial(nombre, hoy):
    vencida = random.random() < 0.2
    fecha_obtencion = hoy - timedelta(days=random.randint(400, 1000))
    if vencida:
        # vigencia corta ya consumida: cualquier fecha entre la obtencion y hoy queda en el pasado
        fecha_caducidad = fecha_obtencion + timedelta(days=random.randint(30, 300))
    else:
        fecha_caducidad = hoy + timedelta(days=random.randint(30, 700))
    return CredencialProfesional(nombre, fecha_obtencion, fecha_caducidad)


def construir_lista_categorias(n_trabajadores):
    categorias = []
    for categoria, proporcion in PROPORCION_CATEGORIAS.items():
        categorias.extend([categoria] * round(n_trabajadores * proporcion))
    while len(categorias) < n_trabajadores:
        categorias.append("Tecnico")
    return categorias[:n_trabajadores]


def construir_trabajadores(habilidades_por_nombre, hoy):
    categorias = construir_lista_categorias(N_TRABAJADORES)
    random.shuffle(categorias)
    trabajadores = []
    for id_trabajador in range(1, N_TRABAJADORES + 1):
        categoria = categorias[id_trabajador - 1]
        horas_maximas = HORAS_MAXIMAS_POR_CATEGORIA[categoria]

        n_habilidades = random.randint(1, 5)
        nombres_habilidades = random.sample(NOMBRES_HABILIDADES, n_habilidades)
        habilidades = [
            HabilidadDeTrabajador(habilidades_por_nombre[nombre], random.choice(
                [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO]
            ))
            for nombre in nombres_habilidades
        ]

        n_credenciales = random.randint(1, min(4, len(NOMBRES_CREDENCIALES)))
        nombres_credenciales = random.sample(NOMBRES_CREDENCIALES, n_credenciales)
        credenciales = [generar_credencial(nombre, hoy) for nombre in nombres_credenciales]

        nombre_trabajador = f"Trabajador {id_trabajador:03d}"
        clase = Supervisor if categoria == "Supervisor" else Trabajador
        trabajador = clase(
            id_trabajador, nombre_trabajador, habilidades, credenciales, horas_maximas,
            categoria=categoria,
        )
        trabajadores.append(trabajador)
    return trabajadores


def categorizar_conflicto(excepcion):
    if isinstance(excepcion, TrabajadorNoAptoError):
        if excepcion.habilidades_faltantes:
            return "FALTA_HABILIDAD"
        return "CREDENCIAL_VENCIDA"
    if isinstance(excepcion, HorasMaximasExcedidasError):
        return "HORAS_EXCEDIDAS"
    if isinstance(excepcion, FranjaSinLugarError):
        return "FRANJA_COMPLETA"
    if isinstance(excepcion, AsignacionDuplicadaError):
        return "LABOR_YA_ASIGNADA"
    return "DESCONOCIDO"


def trabajador_compatible(trabajador, labor, fecha):
    area = labor.get_area()
    return (
        trabajador.tiene_habilidades(labor.get_habilidades_requeridas())
        and trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha)
        and trabajador.tiene_credenciales_activas(area.get_credenciales_obligatorias(), fecha)
    )


def construir_candidatos_por_labor(trabajadores, labores, hoy):
    # aproximacion con la fecha de hoy: alcanza para elegir una pareja labor/trabajador
    # plausible: la aptitud real se vuelve a validar en el constructor de Asignacion
    return {
        labor.get_id(): [t for t in trabajadores if trabajador_compatible(t, labor, hoy)]
        for labor in labores
    }


def generar_asignaciones(sistema, trabajadores, labores, hoy):
    # Igual que en el core (regla 12), las horas maximas son un tope SEMANAL: se simula
    # semana a semana reiniciando horas_asignadas, en vez de acumular 90 dias seguidos
    # (eso disparaba HORAS_EXCEDIDAS en casi cualquier intento despues de la primera semana).
    estados = [EstadoAsignacion.APROBADA, EstadoAsignacion.AUTOMATICA, EstadoAsignacion.PENDIENTE]
    pesos_estado = [0.5, 0.3, 0.2]

    candidatos_por_labor = construir_candidatos_por_labor(trabajadores, labores, hoy)
    labores_viables = [labor for labor in labores if candidatos_por_labor[labor.get_id()]]
    if not labores_viables:
        labores_viables = labores

    conflictos = []
    slots_usados = []

    n_semanas = max(1, DIAS_HISTORIA // 7)
    objetivo_por_semana = max(1, -(-ASIGNACIONES_OBJETIVO // n_semanas))  # redondeo hacia arriba
    tope_intentos_semana = max(50, INTENTOS_MAXIMOS // n_semanas)
    fecha_inicio_total = hoy - timedelta(days=DIAS_HISTORIA)

    with redirect_stdout(io.StringIO()):
        for semana in range(n_semanas):
            if len(sistema.asignaciones) >= ASIGNACIONES_OBJETIVO:
                break
            if semana > 0:
                sistema.reiniciar_horas_trabajadores()

            fecha_inicio_semana = fecha_inicio_total + timedelta(days=7 * semana)
            asignaciones_al_empezar_semana = len(sistema.asignaciones)
            intentos_semana = 0

            while (
                len(sistema.asignaciones) - asignaciones_al_empezar_semana < objetivo_por_semana
                and intentos_semana < tope_intentos_semana
                and len(sistema.asignaciones) < ASIGNACIONES_OBJETIVO
            ):
                intentos_semana += 1
                forzar_conflicto = random.random() < PROBABILIDAD_INTENTO_SIN_FILTRAR

                if slots_usados and random.random() < PROBABILIDAD_REUTILIZAR_SLOT:
                    _, labor, franja, fecha = random.choice(slots_usados)
                    trabajador = random.choice(trabajadores)
                elif forzar_conflicto:
                    labor = random.choice(labores)
                    franja = random.choice(labor.get_area().get_franjas())
                    fecha = fecha_inicio_semana + timedelta(days=random.randint(0, 6))
                    trabajador = random.choice(trabajadores)
                else:
                    labor = random.choice(labores_viables)
                    franja = random.choice(labor.get_area().get_franjas())
                    fecha = fecha_inicio_semana + timedelta(days=random.randint(0, 6))
                    trabajador = random.choice(candidatos_por_labor[labor.get_id()])

                estado = random.choices(estados, weights=pesos_estado)[0]

                try:
                    asignacion = Asignacion(trabajador, labor, franja, fecha, sistema.asignaciones, estado=estado)
                except (TrabajadorNoAptoError, HorasMaximasExcedidasError, FranjaSinLugarError, AsignacionDuplicadaError) as error:
                    conflictos.append({
                        "id": len(conflictos) + 1,
                        "tipo_conflicto": categorizar_conflicto(error),
                        "trabajador_id": trabajador.get_id(),
                        "labor_id": labor.get_id(),
                        "area": labor.get_area().get_nombre(),
                        "franja": franja.get_nombre(),
                        "fecha": fecha.isoformat(),
                        "detalle": str(error),
                    })
                else:
                    sistema.asignaciones.append(asignacion)
                    sistema.registrar_ocupacion(fecha, franja, labor.get_area())
                    sistema.registrar_en_bitacora(TipoAccionBitacora.PROPUESTA, labor, trabajador)
                    if estado == EstadoAsignacion.APROBADA:
                        sistema.registrar_en_bitacora(TipoAccionBitacora.APROBACION, labor, trabajador)
                    slots_usados.append((trabajador, labor, franja, fecha))

    if len(sistema.asignaciones) < ASIGNACIONES_OBJETIVO:
        print(f"Aviso: se llego al limite de intentos con {len(sistema.asignaciones)} asignaciones exitosas (objetivo {ASIGNACIONES_OBJETIVO}).")

    return conflictos


def guardar_conflictos(conflictos, directorio):
    os.makedirs(directorio, exist_ok=True)
    ruta = os.path.join(directorio, "conflictos.csv")
    columnas = ["id", "tipo_conflicto", "trabajador_id", "labor_id", "area", "franja", "fecha", "detalle"]
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(conflictos)
    return ruta


def main():
    hoy = date.today()

    habilidades_por_nombre = construir_habilidades()
    areas = construir_areas()
    labores = construir_labores(areas, habilidades_por_nombre)
    trabajadores = construir_trabajadores(habilidades_por_nombre, hoy)

    sistema = Sistema(trabajadores=trabajadores, areas=areas, labores=labores)

    conflictos = generar_asignaciones(sistema, trabajadores, labores, hoy)

    sistema.guardar_todo(directorio=DIRECTORIO_DATOS)
    ruta_conflictos = guardar_conflictos(conflictos, DIRECTORIO_DATOS)

    conteo_por_tipo = {}
    for conflicto in conflictos:
        tipo = conflicto["tipo_conflicto"]
        conteo_por_tipo[tipo] = conteo_por_tipo.get(tipo, 0) + 1

    print("Dataset generado en:", DIRECTORIO_DATOS)
    print(f"  Trabajadores: {len(trabajadores)} (de los cuales {sum(1 for t in trabajadores if isinstance(t, Supervisor))} supervisores)")
    print(f"  Areas: {len(areas)}")
    print(f"  Labores: {len(labores)}")
    print(f"  Asignaciones exitosas: {len(sistema.asignaciones)}")
    print(f"  Conflictos registrados: {len(conflictos)} -> {ruta_conflictos}")
    print("  Conflictos por tipo:")
    for tipo, cantidad in sorted(conteo_por_tipo.items(), key=lambda par: -par[1]):
        print(f"    {tipo}: {cantidad}")


if __name__ == "__main__":
    main()
