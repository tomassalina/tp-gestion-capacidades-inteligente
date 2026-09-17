class Labor:

    def __init__(self, id, titulo, descripcion, duracion_horas, habilidades_requeridas, credenciales_requeridas, area):
        if duracion_horas <= 0:
            raise ValueError("La duracion en horas debe ser mayor a 0")

        self._id = id
        self._titulo = titulo
        self._descripcion = descripcion
        self._duracion_horas = duracion_horas
        self._habilidades_requeridas = habilidades_requeridas
        self._credenciales_requeridas = credenciales_requeridas
        self._area = area

    def get_id(self):
        return self._id

    def get_titulo(self):
        return self._titulo

    def set_titulo(self, titulo):
        self._titulo = titulo

    def get_descripcion(self):
        return self._descripcion

    def set_descripcion(self, descripcion):
        self._descripcion = descripcion

    def get_duracion_horas(self):
        return self._duracion_horas

    def set_duracion_horas(self, duracion_horas):
        self._duracion_horas = duracion_horas

    def get_habilidades_requeridas(self):
        return self._habilidades_requeridas

    def set_habilidades_requeridas(self, habilidades_requeridas):
        self._habilidades_requeridas = habilidades_requeridas

    def get_credenciales_requeridas(self):
        return self._credenciales_requeridas

    def set_credenciales_requeridas(self, credenciales_requeridas):
        self._credenciales_requeridas = credenciales_requeridas

    def get_area(self):
        return self._area

    def set_area(self, area):
        self._area = area
