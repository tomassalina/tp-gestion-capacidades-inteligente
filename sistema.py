from asignacion import Asignacion


class Sistema:
    """Automatiza, una vez por semana, el procesamiento de solicitudes de asignacion
    y el reinicio de las horas de los trabajadores. Un Supervisor puede disparar
    estas mismas acciones manualmente a traves de sus propios metodos."""

    def __init__(self, trabajadores=None, areas=None, labores=None):
        self._trabajadores = trabajadores or []
        self._areas = areas or []
        self._labores = labores or []
        self._solicitudes_pendientes = []

    def get_trabajadores(self):
        return self._trabajadores

    def set_trabajadores(self, trabajadores):
        self._trabajadores = trabajadores

    def get_areas(self):
        return self._areas

    def set_areas(self, areas):
        self._areas = areas

    def get_labores(self):
        return self._labores

    def set_labores(self, labores):
        self._labores = labores

    def get_asignaciones(self):
        return Asignacion.todas

    def get_solicitudes_pendientes(self):
        return self._solicitudes_pendientes

    def solicitar_asignacion(self, trabajador, labor, franja, fecha):
        self._solicitudes_pendientes.append((trabajador, labor, franja, fecha))

    def ejecutar_acciones_semanales(self):
        self._procesar_solicitudes_pendientes()
        self._reiniciar_horas_trabajadores()

    def _procesar_solicitudes_pendientes(self):
        list(map(lambda solicitud: Asignacion.crear(*solicitud), self._solicitudes_pendientes))
        self._solicitudes_pendientes = []

    def _reiniciar_horas_trabajadores(self):
        list(map(lambda trabajador: trabajador.reiniciar_horas(), self._trabajadores))
