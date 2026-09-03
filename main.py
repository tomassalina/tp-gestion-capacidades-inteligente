from datetime import date

from credencial_profesional import CredencialProfesional
from trabajador import Trabajador
from supervisor import Supervisor
from area_de_trabajo import AreaDeTrabajo
from labor import Labor
from asignacion import Asignacion


if __name__ == "__main__":
    fecha_hoy = date(2026, 9, 2)

    area_cocina = AreaDeTrabajo(
        nombre="Cocina",
        credenciales_obligatorias=["Carnet de Manipulacion de Alimentos"],
        capacidad_por_franja={"Manana": 1, "Tarde": 2, "Noche": 1},
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
        habilidades=["Coccion"],
        credenciales=[credencial_vigente],
        horas_maximas_semana=20,
    )

    beto = Trabajador(
        id=2,
        nombre="Beto",
        habilidades=["Coccion"],
        credenciales=[credencial_vencida],
        horas_maximas_semana=20,
    )

    labor_cocinar = Labor(
        id=1,
        titulo="Preparar almuerzo",
        descripcion="Cocinar el menu del dia",
        duracion_horas=4,
        habilidades_requeridas=["Coccion"],
        credenciales_requeridas=["Carnet de Manipulacion de Alimentos"],
        area=area_cocina,
    )

    print("--- Intento de asignacion para Ana (apta) ---")
    asignacion_ana = Asignacion.crear(ana, labor_cocinar, franja="Manana", fecha=fecha_hoy)

    print("\n--- Intento de asignacion para Beto (credencial vencida) ---")
    Asignacion.crear(beto, labor_cocinar, franja="Manana", fecha=fecha_hoy)

    print("\n--- Un Supervisor formaliza la asignacion de Ana ---")
    carla = Supervisor(
        id=3,
        nombre="Carla",
        habilidades=[],
        credenciales=[],
        horas_maximas_semana=20,
    )
    print(f"Estado antes de aprobar: {asignacion_ana.estado}")
    carla.aprobar_asignacion(asignacion_ana)
    print(f"Estado despues de aprobar: {asignacion_ana.estado}")
