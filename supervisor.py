from trabajador import Trabajador
from asignacion import Asignacion, EstadoAsignacion
from tipo_accion_bitacora import TipoAccionBitacora


class Supervisor(Trabajador):

    def aprobar_asignacion(self, asignacion, sistema=None):
        if sistema is not None:
            sistema.aprobar_asignacion(asignacion)
        else:
            asignacion.aprobar()

    def ejecutar_acciones_del_sistema(self, sistema):
        sistema.ejecutar_acciones_semanales()

    def aprobar_asignaciones_pendientes(self, sistema):
        for asignacion in sistema.obtener_asignaciones():
            if asignacion.get_estado() == EstadoAsignacion.PENDIENTE:
                self.aprobar_asignacion(asignacion, sistema)

    def reasignar_asignacion(self, asignacion, nuevo_trabajador):
        asignacion.reasignar(nuevo_trabajador)

    def rechazar_asignacion(self, asignacion, sistema):
        sistema.revertir_asignacion(asignacion)

    def agregar_regla_area(self, area, credencial):
        area.agregar_credencial_obligatoria(credencial)

    def asignar_trabajador(self, sistema, trabajador, labor, franja, fecha):
        nueva_asignacion = Asignacion(
            trabajador, labor, franja, fecha, sistema.obtener_asignaciones(), estado=EstadoAsignacion.APROBADA
        )
        sistema.obtener_asignaciones().append(nueva_asignacion)
        sistema.registrar_ocupacion(fecha, franja, labor.get_area())
        sistema.registrar_en_bitacora(TipoAccionBitacora.PROPUESTA, labor, trabajador)
        sistema.registrar_en_bitacora(TipoAccionBitacora.APROBACION, labor, trabajador)
        return nueva_asignacion

    @staticmethod
    def cargar_todos(repo, habilidades_por_nombre):
        return list(map(lambda fila: Trabajador.desde_fila(fila, habilidades_por_nombre, Supervisor), repo.find_all()))
