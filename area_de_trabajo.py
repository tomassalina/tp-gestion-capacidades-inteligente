class AreaDeTrabajo:

    def __init__(self, nombre, credenciales_obligatorias, capacidad_por_franja):
        self.nombre = nombre
        self.credenciales_obligatorias = credenciales_obligatorias
        self.capacidad_por_franja = capacidad_por_franja
        self.trabajadores_por_franja = {}

    def tiene_lugar(self, franja):
        ocupados = self.trabajadores_por_franja.get(franja, 0)
        capacidad = self.capacidad_por_franja.get(franja, 0)
        return ocupados < capacidad

    def ocupar_lugar(self, franja):
        self.trabajadores_por_franja[franja] = self.trabajadores_por_franja.get(franja, 0) + 1
