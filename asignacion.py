class Asignacion:

    todas = []

    def __init__(self, trabajador, labor, franja, fecha):
        self._trabajador = trabajador
        self._labor = labor
        self._franja = franja
        self._fecha = fecha
        self._estado = "Pendiente"

    def get_trabajador(self):
        return self._trabajador

    def get_labor(self):
        return self._labor

    def get_franja(self):
        return self._franja

    def get_fecha(self):
        return self._fecha

    def get_estado(self):
        return self._estado

    def set_estado(self, estado):
        self._estado = estado

    @staticmethod
    def es_apto(trabajador, labor, franja, fecha):
        reglas = [
            (
                lambda: trabajador.tiene_habilidades(labor.get_habilidades_requeridas()),
                f"{trabajador.get_nombre()} no tiene todas las habilidades requeridas por la labor '{labor.get_titulo()}'",
            ),
            (
                lambda: trabajador.tiene_credenciales_activas(labor.get_credenciales_requeridas(), fecha),
                f"{trabajador.get_nombre()} no tiene las credenciales de la labor activas en la fecha {fecha}",
            ),
            (
                lambda: trabajador.tiene_credenciales_activas(labor.get_area().get_credenciales_obligatorias(), fecha),
                f"{trabajador.get_nombre()} no tiene las credenciales obligatorias del area '{labor.get_area().get_nombre()}' activas",
            ),
            (
                lambda: trabajador.puede_tomar_horas(labor.get_duracion_horas()),
                f"{trabajador.get_nombre()} superaria sus horas maximas semanales ({trabajador.get_horas_maximas_semana()}hs)",
            ),
            (
                lambda: franja.tiene_lugar(),
                f"La franja '{franja.get_nombre()}' del area '{labor.get_area().get_nombre()}' no tiene lugar disponible",
            ),
            (
                lambda: not any(
                    asignacion.get_labor() == labor and asignacion.get_franja() == franja and asignacion.get_fecha() == fecha
                    for asignacion in Asignacion.todas
                ),
                f"La labor '{labor.get_titulo()}' ya tiene una asignacion para la franja '{franja.get_nombre()}' del {fecha}",
            ),
        ]

        motivo_rechazo = next((mensaje for condicion, mensaje in reglas if not condicion()), None)
        if motivo_rechazo:
            print(motivo_rechazo)
            return False
        return True

    @classmethod
    def crear(cls, trabajador, labor, franja, fecha):
        if not cls.es_apto(trabajador, labor, franja, fecha):
            print(f"No se pudo asignar la labor '{labor.get_titulo()}' a {trabajador.get_nombre()}")
            return None

        trabajador.sumar_horas(labor.get_duracion_horas())
        franja.ocupar_lugar()
        nueva_asignacion = cls(trabajador, labor, franja, fecha)
        cls.todas.append(nueva_asignacion)
        print(
            f"Labor '{labor.get_titulo()}' asignada a {trabajador.get_nombre()} "
            f"en la franja '{franja.get_nombre()}' (estado: {nueva_asignacion.get_estado()})"
        )
        return nueva_asignacion

    def aprobar(self):
        self.set_estado("Aprobada")
