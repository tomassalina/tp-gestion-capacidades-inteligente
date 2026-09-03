from trabajador import Trabajador
from labor import Labor
from area_de_trabajo import AreaDeTrabajo


def es_apto_para_labor(trabajador, labor, franja, fecha):
    if not trabajador.tiene_habilidades(labor.habilidades_requeridas):
        print(f"{trabajador.nombre} no tiene todas las habilidades requeridas por la labor '{labor.titulo}'")
        return False

    if not trabajador.tiene_credenciales_activas(labor.credenciales_requeridas, fecha):
        print(f"{trabajador.nombre} no tiene las credenciales de la labor activas en la fecha {fecha}")
        return False

    if not trabajador.tiene_credenciales_activas(labor.area.credenciales_obligatorias, fecha):
        print(f"{trabajador.nombre} no tiene las credenciales obligatorias del area '{labor.area.nombre}' activas")
        return False

    if not trabajador.puede_tomar_horas(labor.duracion_horas):
        print(f"{trabajador.nombre} superaria sus horas maximas semanales ({trabajador.horas_maximas_semana}hs)")
        return False

    if not labor.area.tiene_lugar(franja):
        print(f"El area '{labor.area.nombre}' no tiene lugar disponible en la franja '{franja}'")
        return False

    return True


def asignar_labor(trabajador, labor, franja, fecha):
    if es_apto_para_labor(trabajador, labor, franja, fecha):
        trabajador.horas_asignadas += labor.duracion_horas
        labor.area.ocupar_lugar(franja)
        print(f"Labor '{labor.titulo}' asignada a {trabajador.nombre} en la franja '{franja}'")
    else:
        print(f"No se pudo asignar la labor '{labor.titulo}' a {trabajador.nombre}")
