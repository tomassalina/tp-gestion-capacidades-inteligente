from datetime import date
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from credencial_profesional import CredencialProfesional
from repositorio_csv import codificar_lista, decodificar_lista
from agenda import Agenda


class Trabajador:

    def __init__(self, id, nombre, habilidades, credenciales, horas_maximas_semana, **atributos):
        if not isinstance(id, int):
            raise TypeError("id debe ser un int")
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")
        if not isinstance(habilidades, list) or not all(map(lambda h: isinstance(h, HabilidadDeTrabajador), habilidades)):
            raise TypeError("habilidades debe ser una lista de HabilidadDeTrabajador")
        if not isinstance(credenciales, list) or not all(map(lambda c: isinstance(c, CredencialProfesional), credenciales)):
            raise TypeError("credenciales debe ser una lista de CredencialProfesional")
        if not isinstance(horas_maximas_semana, (int, float)):
            raise TypeError("horas_maximas_semana debe ser un numero")
        if horas_maximas_semana <= 0:
            raise ValueError("Las horas maximas por semana deben ser mayores a 0")

        self.id = id
        self.nombre = nombre
        self.habilidades = []
        self.repertorio_habilidades = set()
        for habilidad_de_trabajador in habilidades:
            self.agregar_habilidad(habilidad_de_trabajador)
        self.credenciales = credenciales
        self.horas_maximas_semana = horas_maximas_semana
        self.horas_asignadas = 0
        self.atributos = atributos
        self.agenda = Agenda()

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre

    def get_habilidades(self):
        return self.habilidades

    def set_habilidades(self, habilidades):
        self.habilidades = []
        self.repertorio_habilidades = set()
        for habilidad_de_trabajador in habilidades:
            self.agregar_habilidad(habilidad_de_trabajador)

    def agregar_habilidad(self, habilidad_de_trabajador):
        if not isinstance(habilidad_de_trabajador, HabilidadDeTrabajador):
            raise TypeError("habilidad_de_trabajador debe ser una instancia de HabilidadDeTrabajador")
        nombre = habilidad_de_trabajador.get_habilidad().get_nombre()
        if nombre in self.repertorio_habilidades:
            return
        self.repertorio_habilidades.add(nombre)
        self.habilidades.append(habilidad_de_trabajador)

    def nombres_habilidades(self):
        return {habilidad_de_trabajador.get_habilidad().get_nombre() for habilidad_de_trabajador in self.habilidades}

    def habilidades_en_comun(self, otro_trabajador):
        return self.nombres_habilidades() & otro_trabajador.nombres_habilidades()

    def habilidades_exclusivas(self, otro_trabajador):
        return self.nombres_habilidades() - otro_trabajador.nombres_habilidades()

    def get_credenciales(self):
        return self.credenciales

    def set_credenciales(self, credenciales):
        self.credenciales = credenciales

    def get_horas_maximas_semana(self):
        return self.horas_maximas_semana

    def set_horas_maximas_semana(self, horas_maximas_semana):
        self.horas_maximas_semana = horas_maximas_semana

    def get_horas_asignadas(self):
        return self.horas_asignadas

    def get_atributos(self):
        return self.atributos

    def get_atributo(self, clave, valor_por_defecto=None):
        return self.atributos.get(clave, valor_por_defecto)

    def tiene_habilidades(self, habilidades_requeridas):
        return all(
            any(
                propia.get_habilidad() == requerida.get_habilidad() and propia.cumple_nivel_minimo(requerida.get_nivel_minimo())
                for propia in self.habilidades
            )
            for requerida in habilidades_requeridas
        )

    def tiene_credenciales_activas(self, credenciales_requeridas, fecha):
        return all(
            any(credencial.get_nombre() == nombre_requerido and credencial.esta_activa(fecha) for credencial in self.credenciales)
            for nombre_requerido in credenciales_requeridas
        )

    def obtener_habilidades_faltantes(self, habilidades_requeridas):
        return {
            requerida.get_habilidad().get_nombre()
            for requerida in habilidades_requeridas
            if not any(
                propia.get_habilidad() == requerida.get_habilidad() and propia.cumple_nivel_minimo(requerida.get_nivel_minimo())
                for propia in self.habilidades
            )
        }

    def obtener_credenciales_faltantes(self, credenciales_requeridas, fecha):
        return {
            nombre_requerido
            for nombre_requerido in credenciales_requeridas
            if not any(credencial.get_nombre() == nombre_requerido and credencial.esta_activa(fecha) for credencial in self.credenciales)
        }

    def puede_tomar_horas(self, horas_a_sumar):
        return self.horas_asignadas + horas_a_sumar <= self.horas_maximas_semana

    def sumar_horas(self, horas):
        self.horas_asignadas += horas

    def restar_horas(self, horas):
        self.horas_asignadas = max(0, self.horas_asignadas - horas)

    def reiniciar_horas(self):
        self.horas_asignadas = 0

    def get_agenda(self):
        return self.agenda

    def agregar_a_agenda(self, asignacion):
        self.agenda.agregar(asignacion)

    def sacar_de_agenda(self, asignacion):
        self.agenda.eliminar(asignacion)

    def solicitar_asignacion(self, sistema, labor, franja, fecha):
        sistema.solicitar_asignacion(self, labor, franja, fecha)

    def atributos_a_texto(self):
        return ";".join(f"{clave}={valor}" for clave, valor in self.atributos.items())

    @staticmethod
    def atributos_desde_texto(texto):
        atributos = {}
        if texto != "":
            for par in texto.split(";"):
                clave, valor = par.split("=", 1)
                atributos[clave] = valor
        return atributos

    def guardar(self, repo):
        repo.create(
            id=self.id,
            nombre=self.nombre,
            habilidades=codificar_lista(self.habilidades, lambda h: h.a_texto()),
            credenciales=codificar_lista(self.credenciales, lambda c: c.a_texto()),
            horas_maximas_semana=self.horas_maximas_semana,
            atributos=self.atributos_a_texto(),
        )

    @staticmethod
    def desde_fila(fila, habilidades_por_nombre, clase):
        habilidades = decodificar_lista(
            fila["habilidades"],
            lambda texto: HabilidadDeTrabajador.desde_texto(texto, habilidades_por_nombre),
        )
        credenciales = decodificar_lista(fila["credenciales"], CredencialProfesional.desde_texto)
        atributos = Trabajador.atributos_desde_texto(fila["atributos"])
        return clase(
            int(fila["id"]),
            fila["nombre"],
            habilidades,
            credenciales,
            float(fila["horas_maximas_semana"]),
            **atributos,
        )

    @staticmethod
    def cargar_todos(repo, habilidades_por_nombre):
        return list(map(lambda fila: Trabajador.desde_fila(fila, habilidades_por_nombre, Trabajador), repo.find_all()))
