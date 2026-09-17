from trabajador import Trabajador


class Supervisor(Trabajador):

    def aprobar_asignacion(self, asignacion):
        asignacion.aprobar()

    def ejecutar_acciones_del_sistema(self, sistema):
        sistema.ejecutar_acciones_semanales()

    def aprobar_asignaciones_pendientes(self, sistema):
        pendientes = filter(lambda asignacion: asignacion.get_estado() == "Pendiente", sistema.get_asignaciones())
        list(map(self.aprobar_asignacion, pendientes))
