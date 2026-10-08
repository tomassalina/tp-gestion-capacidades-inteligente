import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from area_de_trabajo import AreaDeTrabajo
from asignacion import Asignacion
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
    h_python = Habilidad("Python")
    h_sql = Habilidad("SQL")
    h_figma = Habilidad("Figma")
    h_investigacion = Habilidad("Investigacion UX")
    h_aws = Habilidad("AWS")
    h_docker = Habilidad("Docker")
    h_testing = Habilidad("Testing Automatizado")

    franjas_frontend = [Franja(TipoFranja.MANIANA, capacidad=3), Franja(TipoFranja.TARDE, capacidad=3), Franja(TipoFranja.NOCHE, capacidad=1)]
    franjas_backend = [Franja(TipoFranja.MANIANA, capacidad=3), Franja(TipoFranja.TARDE, capacidad=3), Franja(TipoFranja.NOCHE, capacidad=1)]
    franjas_diseno = [Franja(TipoFranja.MANIANA, capacidad=2), Franja(TipoFranja.TARDE, capacidad=2)]
    franjas_infra = [Franja(TipoFranja.MANIANA, capacidad=2), Franja(TipoFranja.TARDE, capacidad=1), Franja(TipoFranja.NOCHE, capacidad=1)]

    area_frontend = AreaDeTrabajo("Frontend Squad", ["NDA Firmado"], franjas_frontend)
    area_backend = AreaDeTrabajo("Backend Squad", ["NDA Firmado"], franjas_backend)
    area_diseno = AreaDeTrabajo("Diseno de Producto", ["NDA Firmado"], franjas_diseno)
    area_infra = AreaDeTrabajo("Infraestructura", ["NDA Firmado", "Certificacion Seguridad Cloud"], franjas_infra)

    labores = [
        Labor(1, "Implementar feature de checkout", "Nueva pantalla de pago en el frontend principal", 4,
              [HabilidadRequerida(h_react, NivelHabilidad.INTERMEDIO)], ["NDA Firmado"], area_frontend),
        Labor(2, "Migrar dashboard a Vue 3", "Actualizacion del panel interno", 4,
              [HabilidadRequerida(h_vue, NivelHabilidad.AVANZADO)], ["NDA Firmado"], area_frontend),
        Labor(3, "API de notificaciones", "Endpoint REST para push y email", 4,
              [HabilidadRequerida(h_node, NivelHabilidad.INTERMEDIO)], ["NDA Firmado"], area_backend),
        Labor(4, "Optimizar queries de reportes", "Tunning de consultas lentas en produccion", 4,
              [HabilidadRequerida(h_sql, NivelHabilidad.AVANZADO)], ["NDA Firmado"], area_backend),
        Labor(5, "Research de onboarding", "Entrevistas a usuarios nuevos", 3,
              [HabilidadRequerida(h_investigacion, NivelHabilidad.BASICO)], ["NDA Firmado"], area_diseno),
        Labor(6, "Prototipo de app movil", "Wireframes y flujo en Figma", 4,
              [HabilidadRequerida(h_figma, NivelHabilidad.INTERMEDIO)], ["NDA Firmado"], area_diseno),
        Labor(7, "Migrar a contenedores", "Dockerizar los servicios core", 4,
              [HabilidadRequerida(h_docker, NivelHabilidad.INTERMEDIO)], ["NDA Firmado", "Certificacion Seguridad Cloud"], area_infra),
        Labor(8, "Pipeline de CI/CD", "Automatizar deploys a AWS", 4,
              [HabilidadRequerida(h_aws, NivelHabilidad.AVANZADO)], ["NDA Firmado", "Certificacion Seguridad Cloud"], area_infra),
    ]

    plantilla_roles = [
        ("Frontend Developer", h_react, area_frontend, 10),
        ("Frontend Developer Jr", h_vue, area_frontend, 4),
        ("Backend Developer", h_node, area_backend, 8),
        ("Backend Developer Jr", h_sql, area_backend, 4),
        ("UX/UI Designer", h_figma, area_diseno, 3),
        ("UX Researcher", h_investigacion, area_diseno, 2),
        ("DevOps Engineer", h_aws, area_infra, 3),
        ("QA Automation", h_testing, area_backend, 2),
    ]

    nombres = [
        "Lucia", "Mateo", "Sofia", "Benjamin", "Valentina", "Tomas", "Martina", "Joaquin",
        "Catalina", "Nicolas", "Agustina", "Santiago", "Florencia", "Franco", "Camila", "Ignacio",
        "Julieta", "Lautaro", "Victoria", "Bautista", "Pilar", "Gonzalo", "Delfina", "Simon",
        "Emilia", "Thiago", "Antonella", "Felipe",
    ]

    trabajadores = []
    nombre_idx = 0
    id_actual = 10
    niveles = [NivelHabilidad.BASICO, NivelHabilidad.INTERMEDIO, NivelHabilidad.AVANZADO]

    for rol, habilidad, area, cantidad in plantilla_roles:
        for i in range(cantidad):
            nombre = nombres[nombre_idx % len(nombres)]
            nombre_idx += 1
            nivel = niveles[i % len(niveles)]
            credenciales = [credencial("NDA Firmado", 400, 1000)]
            if area in (area_infra,):
                vencida = i % 4 == 0
                credenciales.append(credencial("Certificacion Seguridad Cloud", 500, -30 if vencida else 200))
            trabajador = Trabajador(
                id=id_actual,
                nombre=nombre,
                habilidades=[HabilidadDeTrabajador(habilidad, nivel)],
                credenciales=credenciales,
                horas_maximas_semana=[20, 30, 40][i % 3],
                rol=rol,
                area_equipo=area.get_nombre(),
                seniority={NivelHabilidad.BASICO: "Jr", NivelHabilidad.INTERMEDIO: "Semi Sr", NivelHabilidad.AVANZADO: "Sr"}[nivel],
            )
            trabajadores.append(trabajador)
            id_actual += 1

    supervisores = [
        Supervisor(id=1, nombre="Rocio", habilidades=[], credenciales=[credencial("NDA Firmado", 600, 1500)],
                   horas_maximas_semana=35, rol="Engineering Manager", area_equipo="Frontend Squad"),
        Supervisor(id=2, nombre="Diego", habilidades=[], credenciales=[credencial("NDA Firmado", 600, 1500)],
                   horas_maximas_semana=35, rol="Engineering Manager", area_equipo="Backend Squad"),
    ]

    sistema = Sistema(
        trabajadores=trabajadores + supervisores,
        areas=[area_frontend, area_backend, area_diseno, area_infra],
        labores=labores,
    )

    for candidato in trabajadores:
        if candidato in sistema.buscar_trabajadores_disponibles(labores[0], franjas_frontend[0], HOY):
            sistema.solicitar_asignacion(candidato, labores[0], franjas_frontend[0], HOY)
            break

    return sistema, supervisores[0]


if __name__ == "__main__":
    sistema, supervisor = armar_seed()
    print(f"Trabajadores: {len(sistema.get_trabajadores())}")
    print(f"Areas: {len(sistema.get_areas())}")
    print(f"Labores: {len(sistema.get_labores())}")
    print(f"Solicitudes en cola: {len(sistema.get_solicitudes_pendientes())}")
