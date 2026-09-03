class Asignacion:

    def __init__(self, trabajador, labor, franja, fecha):
        self.trabajador = trabajador
        self.labor = labor
        self.franja = franja
        self.fecha = fecha
        self.estado = "Pendiente"

    def aprobar(self):
        self.estado = "Aprobada"
