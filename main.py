from datetime import date

from credencial_profesional import CredencialProfesional
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from franja import Franja
from trabajador import Trabajador
from supervisor import Supervisor
from area_de_trabajo import AreaDeTrabajo
from labor import Labor
from sistema import Sistema


if __name__ == "__main__":
    fecha_hoy = date(2026, 9, 2)

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

    print("--- Registro de personal con atributos opcionales (**kwargs) ---")
    diego = sistema.registrar_personal(
        id=4,
        nombre="Diego",
        horas_max=15,
        idioma="Ingles",
        area_origen="Cordoba",
        turno_preferido="Tarde",
    )
    print(
        f"{diego.get_nombre()} registrado. "
        f"Idioma: {diego.get_atributo('idioma')}, "
        f"area de origen: {diego.get_atributo('area_origen')}, "
        f"certificacion: {diego.get_atributo('certificacion', 'sin certificacion inicial')}"
    )

    print("\n--- Ana y Beto solicitan la labor durante la semana ---")
    sistema.solicitar_asignacion(ana, labor_cocinar, franja_manana, fecha_hoy)
    sistema.solicitar_asignacion(beto, labor_cocinar, franja_manana, fecha_hoy)

    print("\n--- Carla (supervisora) corre manualmente las acciones semanales del sistema ---")
    carla.ejecutar_acciones_del_sistema(sistema)

    print("\n--- Carla aprueba las asignaciones que quedaron pendientes ---")
    carla.aprobar_asignaciones_pendientes(sistema)

    print("\n--- Resultado final ---")
    for asignacion in sistema.get_asignaciones():
        print(f"{asignacion.get_trabajador().get_nombre()} -> {asignacion.get_labor().get_titulo()} ({asignacion.get_estado()})")
