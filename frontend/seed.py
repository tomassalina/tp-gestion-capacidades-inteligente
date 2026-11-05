import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from area_de_trabajo import AreaDeTrabajo
from credencial_profesional import CredencialProfesional
from franja import Franja, TipoFranja
from habilidad import Habilidad, HabilidadDeTrabajador, HabilidadRequerida, NivelHabilidad
from labor import Labor
from sistema import Sistema
from supervisor import Supervisor
from trabajador import Trabajador

HOY = date(2026, 10, 8)


def credencial(nombre, dias_desde_obtencion, dias_hasta_caducar):
    return CredencialProfesional(
        nombre=nombre,
        fecha_obtencion=HOY - timedelta(days=dias_desde_obtencion),
        fecha_caducidad=HOY + timedelta(days=dias_hasta_caducar),
    )


def armar_seed():
    h_react = Habilidad("React")
    h_vue = Habilidad("Vue")
    h_node = Habilidad("Node.js")
    h_sql = Habilidad("SQL")

    franjas_frontend = [Franja(TipoFranja.MANIANA, capacidad=2), Franja(TipoFranja.TARDE, capacidad=2)]
    franjas_backend = [Franja(TipoFranja.MANIANA, capacidad=2), Franja(TipoFranja.TARDE, capacidad=2)]

    area_frontend = AreaDeTrabajo("Frontend Squad", ["NDA Firmado"], franjas_frontend)
    area_backend = AreaDeTrabajo("Backend Squad", ["NDA Firmado"], franjas_backend)

    labores = [
        Labor(1, "Implementar feature de checkout", "Nueva pantalla de pago en el frontend principal", 4,
              [HabilidadRequerida(h_react, NivelHabilidad.INTERMEDIO)], ["NDA Firmado"], area_frontend),
        Labor(2, "Migrar dashboard a Vue 3", "Actualizacion del panel interno", 4,
              [HabilidadRequerida(h_vue, NivelHabilidad.AVANZADO)], ["NDA Firmado"], area_frontend),
        Labor(3, "API de notificaciones", "Endpoint REST para push y email", 4,
              [HabilidadRequerida(h_node, NivelHabilidad.INTERMEDIO)], ["NDA Firmado"], area_backend),
        Labor(4, "Optimizar queries de reportes", "Tunning de consultas lentas en produccion", 4,
              [HabilidadRequerida(h_sql, NivelHabilidad.AVANZADO)], ["NDA Firmado"], area_backend),
    ]

    nda_vigente = credencial("NDA Firmado", 400, 1000)

    ana = Trabajador(
        id=1, nombre="Ana",
        habilidades=[HabilidadDeTrabajador(h_react, NivelHabilidad.INTERMEDIO)],
        credenciales=[credencial("NDA Firmado", 400, 1000)],
        horas_maximas_semana=20,
        rol="Frontend Developer", area_equipo="Frontend Squad", seniority="Semi Sr",
    )
    beto = Trabajador(
        id=2, nombre="Beto",
        habilidades=[HabilidadDeTrabajador(h_node, NivelHabilidad.INTERMEDIO)],
        credenciales=[credencial("NDA Firmado", 400, 1000)],
        horas_maximas_semana=30,
        rol="Backend Developer", area_equipo="Backend Squad", seniority="Semi Sr",
    )
    diego = Trabajador(
        id=3, nombre="Diego",
        habilidades=[],
        credenciales=[credencial("NDA Firmado", 400, 1000)],
        horas_maximas_semana=20,
        rol="Frontend Developer Jr", area_equipo="Frontend Squad", seniority="Jr",
    )

    leandro = Supervisor(
        id=4, nombre="Leandro", habilidades=[], credenciales=[credencial("NDA Firmado", 600, 1500)],
        horas_maximas_semana=35, rol="Engineering Manager", area_equipo="Frontend Squad",
    )

    sistema = Sistema(
        trabajadores=[ana, beto, diego, leandro],
        areas=[area_frontend, area_backend],
        labores=labores,
    )

    # Ana ya tiene una solicitud esperando en la cola al arrancar la demo
    ana.solicitar_asignacion(sistema, labores[0], franjas_frontend[0], HOY)

    return sistema, leandro


if __name__ == "__main__":
    sistema, supervisor = armar_seed()
    print(f"Trabajadores: {len(sistema.get_trabajadores())}")
    print(f"Areas: {len(sistema.get_areas())}")
    print(f"Labores: {len(sistema.get_labores())}")
    print(f"Solicitudes en cola: {sistema.get_solicitudes_pendientes().get_cantidad()}")
