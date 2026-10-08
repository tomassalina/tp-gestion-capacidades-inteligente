from datetime import date
from habilidad import Habilidad, NivelHabilidad, HabilidadDeTrabajador, HabilidadRequerida
from credencial_profesional import CredencialProfesional


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

        self._id = id
        self._nombre = nombre
        self._habilidades = habilidades
        self._credenciales = credenciales
        self._horas_maximas_semana = horas_maximas_semana
        self._horas_asignadas = 0
        self._atributos = atributos

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

    def get_atributos(self):
        return self._atributos

    def get_atributo(self, clave, valor_por_defecto=None):
        return self._atributos.get(clave, valor_por_defecto)

    def tiene_habilidades(self, habilidades_requeridas):
        return all(
            any(
                propia.get_habilidad() == requerida.get_habilidad() and propia.cumple_nivel_minimo(requerida.get_nivel_minimo())
                for propia in self._habilidades
            )
            for requerida in habilidades_requeridas
        )

    def tiene_credenciales_activas(self, credenciales_requeridas, fecha):
        return all(
            any(credencial.get_nombre() == nombre_requerido and credencial.esta_activa(fecha) for credencial in self._credenciales)
            for nombre_requerido in credenciales_requeridas
        )

    def puede_tomar_horas(self, horas_a_sumar):
        return self._horas_asignadas + horas_a_sumar <= self._horas_maximas_semana

    def sumar_horas(self, horas):
        self._horas_asignadas += horas

    def restar_horas(self, horas):
        self._horas_asignadas = max(0, self._horas_asignadas - horas)

    def reiniciar_horas(self):
        self._horas_asignadas = 0


def test_horas_maximas_invalidas_lanza_value_error():
    import pytest

    with pytest.raises(ValueError):
        Trabajador(1, "Ana", [], [], 0)


def test_trabajador_tipos_invalidos_lanza_type_error():
    import pytest

    with pytest.raises(TypeError):
        Trabajador("1", "Ana", [], [], 20)
    with pytest.raises(TypeError):
        Trabajador(1, "Ana", "no es lista", [], 20)


def test_trabajador_lista_con_elemento_de_tipo_incorrecto_lanza_type_error():
    import pytest

    with pytest.raises(TypeError):
        Trabajador(1, "Ana", ["no es habilidad"], [], 20)
    with pytest.raises(TypeError):
        Trabajador(1, "Ana", [], ["no es credencial"], 20)


def test_tiene_habilidades_respeta_nivel_minimo():
    soldadura = Habilidad("Soldadura")
    trabajador = Trabajador(1, "Ana", [HabilidadDeTrabajador(soldadura, NivelHabilidad.BASICO)], [], 20)
    requerida_baja = [HabilidadRequerida(soldadura, NivelHabilidad.BASICO)]
    requerida_alta = [HabilidadRequerida(soldadura, NivelHabilidad.AVANZADO)]
    assert trabajador.tiene_habilidades(requerida_baja)
    assert not trabajador.tiene_habilidades(requerida_alta)


def test_puede_tomar_horas_respeta_limite_semanal():
    trabajador = Trabajador(1, "Ana", [], [], 10)
    trabajador.sumar_horas(8)
    assert not trabajador.puede_tomar_horas(4)
    assert trabajador.puede_tomar_horas(2)


def test_restar_horas_nunca_queda_negativo():
    trabajador = Trabajador(1, "Ana", [], [], 10)
    trabajador.sumar_horas(4)
    trabajador.restar_horas(4)
    assert trabajador.get_horas_asignadas() == 0
    trabajador.restar_horas(4)
    assert trabajador.get_horas_asignadas() == 0


def test_atributos_opcionales_por_kwargs():
    trabajador = Trabajador(1, "Diego", [], [], 15, idioma="Ingles")
    assert trabajador.get_atributo("idioma") == "Ingles"
    assert trabajador.get_atributo("inexistente", "default") == "default"


def test_tiene_credenciales_activas_respeta_todas_las_requeridas():
    vigente = CredencialProfesional("Carnet", date(2025, 1, 1), date(2027, 1, 1))
    trabajador = Trabajador(1, "Ana", [], [vigente], 20)
    assert trabajador.tiene_credenciales_activas(["Carnet"], date(2026, 1, 1))
    assert not trabajador.tiene_credenciales_activas(["Carnet", "Otra"], date(2026, 1, 1))
