from trabajador import Trabajador


class Supervisor(Trabajador):

    def aprobar_asignacion(self, asignacion):
        asignacion.aprobar()
