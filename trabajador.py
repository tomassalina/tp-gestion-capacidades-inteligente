class Trabajador:

    def __init__(self, id, nombre, habilidades, credenciales, horas_maximas_semana):
        if horas_maximas_semana <= 0:
            raise ValueError("Las horas maximas por semana deben ser mayores a 0")

        self._id = id
        self._nombre = nombre
        self._habilidades = habilidades
        self._credenciales = credenciales
        self._horas_maximas_semana = horas_maximas_semana
        self._horas_asignadas = 0

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_habilidades(self):
        return self._habilidades

    def set_habilidades(self, habilidades):
        self._habilidades = habilidades

    def get_credenciales(self):
        return self._credenciales

    def set_credenciales(self, credenciales):
        self._credenciales = credenciales

    def get_horas_maximas_semana(self):
        return self._horas_maximas_semana

    def set_horas_maximas_semana(self, horas_maximas_semana):
        self._horas_maximas_semana = horas_maximas_semana

    def get_horas_asignadas(self):
        return self._horas_asignadas

    def tiene_habilidades(self, habilidades_requeridas):
        return all(map(
            lambda requerida: any(
                propia.get_habilidad() == requerida.get_habilidad()
                and propia.cumple_nivel_minimo(requerida.get_nivel_minimo())
                for propia in self._habilidades
            ),
            habilidades_requeridas,
        ))

    def tiene_credenciales_activas(self, credenciales_requeridas, fecha):
        return all(map(
            lambda nombre_requerido: any(
                credencial.get_nombre() == nombre_requerido and credencial.esta_activa(fecha)
                for credencial in self._credenciales
            ),
            credenciales_requeridas,
        ))

    def puede_tomar_horas(self, horas_a_sumar):
        return self._horas_asignadas + horas_a_sumar <= self._horas_maximas_semana

    def sumar_horas(self, horas):
        self._horas_asignadas += horas

    def reiniciar_horas(self):
        self._horas_asignadas = 0
