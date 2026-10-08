from trabajador import Trabajador
from asignacion import Asignacion, EstadoAsignacion


class Supervisor(Trabajador):

    def aprobar_asignacion(self, asignacion):
        asignacion.aprobar()

    def ejecutar_acciones_del_sistema(self, sistema):
        sistema.ejecutar_acciones_semanales()

    def aprobar_asignaciones_pendientes(self, sistema):
        for asignacion in sistema.obtener_asignaciones():
            if asignacion.get_estado() == EstadoAsignacion.PENDIENTE:
                self.aprobar_asignacion(asignacion)

    def reasignar_asignacion(self, asignacion, nuevo_trabajador):
        asignacion.reasignar(nuevo_trabajador)

    def rechazar_asignacion(self, asignacion, sistema):
        asignacion.rechazar()
        sistema.obtener_asignaciones().remove(asignacion)

    def agregar_regla_area(self, area, credencial):
        area.agregar_credencial_obligatoria(credencial)

    def asignar_trabajador(self, sistema, trabajador, labor, franja, fecha):
        nueva_asignacion = Asignacion(
            trabajador, labor, franja, fecha, sistema.obtener_asignaciones(), estado=EstadoAsignacion.APROBADA
        )
        sistema.obtener_asignaciones().append(nueva_asignacion)
        return nueva_asignacion
