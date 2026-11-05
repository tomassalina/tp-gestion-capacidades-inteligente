import os
from datetime import date, datetime
from asignacion import Asignacion, EstadoAsignacion, TrabajadorNoAptoError, HorasMaximasExcedidasError, FranjaSinLugarError, AsignacionDuplicadaError
from trabajador import Trabajador
from supervisor import Supervisor
from habilidad import Habilidad
from area_de_trabajo import AreaDeTrabajo
from labor import Labor
from cola import Cola
from repositorio_csv import RepositorioCSV
from tipo_accion_bitacora import TipoAccionBitacora

ERRORES_ASIGNACION = (TrabajadorNoAptoError, HorasMaximasExcedidasError, FranjaSinLugarError, AsignacionDuplicadaError)

DIRECTORIO_DATOS_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

COLUMNAS_HABILIDADES = ["id", "nombre"]
COLUMNAS_AREAS = ["id", "nombre", "credenciales_obligatorias", "franjas"]
COLUMNAS_LABORES = ["id", "titulo", "descripcion", "duracion_horas", "habilidades_requeridas", "credenciales_requeridas", "area"]
COLUMNAS_TRABAJADORES = ["id", "nombre", "habilidades", "credenciales", "horas_maximas_semana", "atributos"]
COLUMNAS_ASIGNACIONES = ["id", "trabajador_id", "labor_id", "franja", "fecha", "estado"]
COLUMNAS_COLA = ["id", "trabajador_id", "labor_id", "franja", "fecha"]


def armar_repos(directorio):
    os.makedirs(directorio, exist_ok=True)
    return {
        "habilidades": RepositorioCSV(os.path.join(directorio, "habilidades.csv"), COLUMNAS_HABILIDADES),
        "areas": RepositorioCSV(os.path.join(directorio, "areas.csv"), COLUMNAS_AREAS),
        "labores": RepositorioCSV(os.path.join(directorio, "labores.csv"), COLUMNAS_LABORES),
        "trabajadores": RepositorioCSV(os.path.join(directorio, "trabajadores.csv"), COLUMNAS_TRABAJADORES),
        "supervisores": RepositorioCSV(os.path.join(directorio, "supervisores.csv"), COLUMNAS_TRABAJADORES),
        "asignaciones": RepositorioCSV(os.path.join(directorio, "asignaciones.csv"), COLUMNAS_ASIGNACIONES),
        "cola_pendientes": RepositorioCSV(os.path.join(directorio, "cola_pendientes.csv"), COLUMNAS_COLA),
    }

class Sistema:

    def __init__(self, trabajadores=None, areas=None, labores=None):
        if trabajadores is not None and (not isinstance(trabajadores, list) or not all(map(lambda t: isinstance(t, Trabajador), trabajadores))):
            raise TypeError("trabajadores debe ser una lista de Trabajador")
        if areas is not None and (not isinstance(areas, list) or not all(map(lambda a: isinstance(a, AreaDeTrabajo), areas))):
            raise TypeError("areas debe ser una lista de AreaDeTrabajo")
        if labores is not None and (not isinstance(labores, list) or not all(map(lambda l: isinstance(l, Labor), labores))):
            raise TypeError("labores debe ser una lista de Labor")
        self.trabajadores = trabajadores or []
        self.areas = areas or []
        self.labores = labores or []
        self.solicitudes_pendientes, self.asignaciones = Cola(), []
        self.trabajadores_por_id = {}
        self.ocupacion = {}
        self.bitacora = []
        self.reindexar_trabajadores()

    def get_trabajadores(self):
        return self.trabajadores

    def reindexar_trabajadores(self):
        self.trabajadores_por_id = {}
        for trabajador in self.trabajadores:
            self.trabajadores_por_id[trabajador.get_id()] = trabajador

    def buscar_trabajador_por_id(self, id):
        return self.trabajadores_por_id.get(id)

    def set_trabajadores(self, trabajadores):
        self.trabajadores = trabajadores
        self.reindexar_trabajadores()

    def get_areas(self):
        return self.areas

    def set_areas(self, areas):
        self.areas = areas

    def get_labores(self):
        return self.labores

    def set_labores(self, labores):
        self.labores = labores

    def obtener_asignaciones(self):
        return self.asignaciones

    def clave_ocupacion(self, fecha, franja, area):
        # tupla comun como clave compuesta: inmutable, y alcanza para identificar el momento y lugar
        return (fecha, franja, area)

    def registrar_ocupacion(self, fecha, franja, area):
        clave = self.clave_ocupacion(fecha, franja, area)
        self.ocupacion[clave] = self.ocupacion.get(clave, 0) + 1

    def liberar_ocupacion(self, fecha, franja, area):
        clave = self.clave_ocupacion(fecha, franja, area)
        if clave in self.ocupacion:
            self.ocupacion[clave] = max(0, self.ocupacion[clave] - 1)

    def contar_ocupacion(self, fecha, franja, area):
        return self.ocupacion.get(self.clave_ocupacion(fecha, franja, area), 0)

    def registrar_en_bitacora(self, tipo_accion, labor, trabajador):
        registro = (datetime.now(), tipo_accion, labor, trabajador)
        self.bitacora.append(registro)
        return registro

    def obtener_bitacora(self):
        return tuple(self.bitacora)

    def aprobar_asignacion(self, asignacion):
        asignacion.aprobar()
        self.registrar_en_bitacora(TipoAccionBitacora.APROBACION, asignacion.get_labor(), asignacion.get_trabajador())

    def revertir_asignacion(self, asignacion):
        asignacion.rechazar()
        if asignacion in self.asignaciones:
            self.asignaciones.remove(asignacion)
        self.liberar_ocupacion(asignacion.get_fecha(), asignacion.get_franja(), asignacion.get_labor().get_area())
        self.registrar_en_bitacora(TipoAccionBitacora.REVERSION, asignacion.get_labor(), asignacion.get_trabajador())

    def get_solicitudes_pendientes(self):
        return self.solicitudes_pendientes

    def solicitar_asignacion(self, trabajador, labor, franja, fecha):
        if trabajador not in self.buscar_trabajadores_disponibles(labor, franja, fecha):
            raise TrabajadorNoAptoError(
                f"{trabajador.get_nombre()} no es apto para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}'"
            )
        if self.ya_esta_en_la_cola(trabajador, labor, franja, fecha):
            raise AsignacionDuplicadaError(
                f"{trabajador.get_nombre()} ya tiene una solicitud pendiente para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}' el {fecha}"
            )
        self.solicitudes_pendientes.encolar((trabajador, labor, franja, fecha))

    def ya_esta_en_la_cola(self, trabajador, labor, franja, fecha):
        for solicitud in self.solicitudes_pendientes.recorrer():
            trabajador_en_cola, labor_en_cola, franja_en_cola, fecha_en_cola = solicitud
            if trabajador_en_cola == trabajador and labor_en_cola == labor and franja_en_cola == franja and fecha_en_cola == fecha:
                return True
        return False

    def registrar_personal(self, id, nombre, horas_max, **atributos):
        nuevo_trabajador = Trabajador(
            id=id,
            nombre=nombre,
            habilidades=[],
            credenciales=[],
            horas_maximas_semana=horas_max,
            **atributos,
        )
        self.trabajadores.append(nuevo_trabajador)
        self.trabajadores_por_id[nuevo_trabajador.get_id()] = nuevo_trabajador
        return nuevo_trabajador

    def ejecutar_acciones_semanales(self):
        self.procesar_solicitudes_pendientes()
        self.reiniciar_horas_trabajadores()

    def procesar_solicitudes_pendientes(self):
        while not self.solicitudes_pendientes.esta_vacia():
            trabajador, labor, franja, fecha = self.solicitudes_pendientes.desencolar()
            try:
                nueva_asignacion = Asignacion(trabajador, labor, franja, fecha, self.asignaciones)
            except ERRORES_ASIGNACION as e:
                print(f"No se pudo procesar la solicitud de {trabajador.get_nombre()} para '{labor.get_titulo()}': {e}")
            else:
                self.asignaciones.append(nueva_asignacion)
                self.registrar_ocupacion(fecha, franja, labor.get_area())
                self.registrar_en_bitacora(TipoAccionBitacora.PROPUESTA, labor, trabajador)

    def reiniciar_horas_trabajadores(self):
        for trabajador in self.trabajadores:
            trabajador.reiniciar_horas()

    def tiene_asignacion_aprobada(self, labor, franja, fecha):
        for asignacion in self.asignaciones:
            if asignacion.get_labor() == labor and asignacion.get_franja() == franja and asignacion.get_fecha() == fecha:
                if asignacion.get_estado() == EstadoAsignacion.APROBADA:
                    return True
        return False

    def trabajador_esta_disponible(self, trabajador, labor, franja, fecha):
        apto_habilidades = trabajador.tiene_habilidades(labor.get_habilidades_requeridas())
        apto_credenciales_labor = trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha)
        apto_credenciales_area = trabajador.tiene_credenciales_activas(labor.get_area().get_credenciales_obligatorias(), fecha)
        if not (apto_habilidades and apto_credenciales_labor and apto_credenciales_area):
            return False
        if not trabajador.puede_tomar_horas(labor.get_duracion_horas()):
            return False
        if Asignacion.contar_ocupantes(self.asignaciones, franja, labor.get_area(), fecha) >= franja.get_capacidad():
            return False
        if self.tiene_asignacion_aprobada(labor, franja, fecha):
            return False
        return True

    def buscar_trabajadores_disponibles(self, labor, franja, fecha):
        return list(filter(lambda trabajador: self.trabajador_esta_disponible(trabajador, labor, franja, fecha), self.trabajadores))

    def generar_sugerencias(self, fecha):
        nuevas_sugerencias = []
        for labor in self.labores:
            for franja in labor.get_area().get_franjas():
                if self.tiene_asignacion_aprobada(labor, franja, fecha):
                    continue
                candidatos = self.buscar_trabajadores_disponibles(labor, franja, fecha)
                if len(candidatos) == 0:
                    continue
                candidato = candidatos[0]
                try:
                    sugerencia = Asignacion(candidato, labor, franja, fecha, self.asignaciones, estado=EstadoAsignacion.AUTOMATICA)
                except ERRORES_ASIGNACION as e:
                    print(f"No se pudo generar sugerencia para '{labor.get_titulo()}' en la franja '{franja.get_nombre()}': {e}")
                else:
                    self.asignaciones.append(sugerencia)
                    self.registrar_ocupacion(fecha, franja, labor.get_area())
                    self.registrar_en_bitacora(TipoAccionBitacora.PROPUESTA, labor, candidato)
                    nuevas_sugerencias.append(sugerencia)
        return nuevas_sugerencias

    def ciclo_semanal(self, fecha):
        self.asignaciones = []
        self.ocupacion = {}
        self.reiniciar_horas_trabajadores()
        self.procesar_solicitudes_pendientes()
        return self.generar_sugerencias(fecha)

    def recolectar_habilidades(self):
        # las Habilidad son compartidas (Trabajador y Labor apuntan a la misma por nombre),
        # asi que se juntan y deduplican por nombre antes de guardarlas una sola vez
        habilidades_por_nombre = {
            habilidad_de_trabajador.get_habilidad().get_nombre(): habilidad_de_trabajador.get_habilidad()
            for trabajador in self.trabajadores
            for habilidad_de_trabajador in trabajador.get_habilidades()
        }
        habilidades_por_nombre.update({
            habilidad_requerida.get_habilidad().get_nombre(): habilidad_requerida.get_habilidad()
            for labor in self.labores
            for habilidad_requerida in labor.get_habilidades_requeridas()
        })
        return list(habilidades_por_nombre.values())

    def guardar_todo(self, directorio=DIRECTORIO_DATOS_DEFAULT):
        repos = armar_repos(directorio)

        # guardar_todo es una foto completa del sistema, no un agregado: antes de
        # escribir se vacia cada csv, sino una segunda corrida choca con ids ya guardados
        for repo in repos.values():
            repo.escribir_filas([])

        for habilidad in self.recolectar_habilidades():
            habilidad.guardar(repos["habilidades"])

        for area in self.areas:
            area.guardar(repos["areas"])

        for labor in self.labores:
            labor.guardar(repos["labores"])

        for trabajador in self.trabajadores:
            if isinstance(trabajador, Supervisor):
                trabajador.guardar(repos["supervisores"])
            else:
                trabajador.guardar(repos["trabajadores"])

        for asignacion in self.asignaciones:
            asignacion.guardar(repos["asignaciones"])

        for trabajador, labor, franja, fecha in self.solicitudes_pendientes.recorrer():
            repos["cola_pendientes"].create(
                id=f"{trabajador.get_id()}|{labor.get_id()}|{franja.get_nombre()}|{fecha.isoformat()}",
                trabajador_id=trabajador.get_id(),
                labor_id=labor.get_id(),
                franja=franja.get_nombre(),
                fecha=fecha.isoformat(),
            )

    @staticmethod
    def cargar_todo(directorio=DIRECTORIO_DATOS_DEFAULT):
        repos = armar_repos(directorio)

        habilidades = Habilidad.cargar_todas(repos["habilidades"])
        habilidades_por_nombre = {habilidad.get_nombre(): habilidad for habilidad in habilidades}

        areas = AreaDeTrabajo.cargar_todas(repos["areas"])
        areas_por_nombre = {area.get_nombre(): area for area in areas}

        labores = Labor.cargar_todas(repos["labores"], areas_por_nombre, habilidades_por_nombre)
        labores_por_id = {labor.get_id(): labor for labor in labores}

        trabajadores = Trabajador.cargar_todos(repos["trabajadores"], habilidades_por_nombre)
        supervisores = Supervisor.cargar_todos(repos["supervisores"], habilidades_por_nombre)
        todos_los_trabajadores = trabajadores + supervisores
        trabajadores_por_id = {trabajador.get_id(): trabajador for trabajador in todos_los_trabajadores}

        sistema = Sistema(trabajadores=todos_los_trabajadores, areas=areas, labores=labores)

        asignaciones = Asignacion.cargar_todas(repos["asignaciones"], trabajadores_por_id, labores_por_id)
        sistema.obtener_asignaciones().extend(asignaciones)
        for asignacion in asignaciones:
            sistema.registrar_ocupacion(asignacion.get_fecha(), asignacion.get_franja(), asignacion.get_labor().get_area())

        for fila in repos["cola_pendientes"].find_all():
            trabajador = trabajadores_por_id[int(fila["trabajador_id"])]
            labor = labores_por_id[int(fila["labor_id"])]
            franja = labor.get_area().buscar_franja(fila["franja"])
            fecha = date.fromisoformat(fila["fecha"])
            sistema.get_solicitudes_pendientes().encolar((trabajador, labor, franja, fecha))

        return sistema
