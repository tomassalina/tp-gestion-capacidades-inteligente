class Usuario:
    def __init__(self, nombre, apellido, email, fecha_de_alta):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.fecha_de_alta = fecha_de_alta

    def saludar(self):
        print(self.nombre)
