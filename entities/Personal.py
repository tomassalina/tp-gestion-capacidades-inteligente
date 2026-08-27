from .Usuario import Usuario

class Personal(Usuario):
    def __init__(
        self, 
        nombre, 
        apellido, 
        email, 
        fecha_de_alta, 
        maximo_horas_por_semana,
        habilidades = [], 
        credenciales = [],
    ):
        super().__init__(nombre, apellido, email, fecha_de_alta)

        self.maximo_horas_por_semana = maximo_horas_por_semana
        self.habilidades = habilidades
        self.credenciales = credenciales

        self.disponible = True

        self.saludar()

