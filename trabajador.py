from credencial_profesional import CredencialProfesional


class Trabajador:

    def __init__(self, id, nombre, habilidades, credenciales, horas_maximas_semana):
        if horas_maximas_semana <= 0:
            raise ValueError("Las horas maximas por semana deben ser mayores a 0")

        self.id = id
        self.nombre = nombre
        self.habilidades = habilidades
        self.credenciales = credenciales
        self.horas_maximas_semana = horas_maximas_semana
        self.horas_asignadas = 0

    def tiene_habilidades(self, habilidades_requeridas):
        return all(habilidad in self.habilidades for habilidad in habilidades_requeridas)

    def tiene_credenciales_activas(self, credenciales_requeridas, fecha):
        for nombre_requerido in credenciales_requeridas:
            credencial_encontrada = next(
                (c for c in self.credenciales if c.nombre == nombre_requerido),
                None,
            )
            if credencial_encontrada is None or not credencial_encontrada.esta_activa(fecha):
                return False
        return True

    def puede_tomar_horas(self, horas_a_sumar):
        return self.horas_asignadas + horas_a_sumar <= self.horas_maximas_semana

    def reiniciar_horas(self):
        self.horas_asignadas = 0
