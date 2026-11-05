from datetime import date

import pytest

from agenda import Agenda
from area_de_trabajo import AreaDeTrabajo
from franja import Franja, TipoFranja
from labor import Labor


@pytest.fixture
def labor_de_prueba():
    franja_manana = Franja(TipoFranja.MANIANA, capacidad=5)
    franja_tarde = Franja(TipoFranja.TARDE, capacidad=5)
    franja_noche = Franja(TipoFranja.NOCHE, capacidad=5)
    area = AreaDeTrabajo("Cocina", [], [franja_manana, franja_tarde, franja_noche])
    labor = Labor(1, "Cocinar", "Cocinar el menu", 4, [], [], area)
    return labor, franja_manana, franja_tarde, franja_noche


class AsignacionFalsa:
    """Doble de Asignacion liviano: solo lo que Agenda necesita (get_fecha/get_franja), sin pasar por validar_apto."""

    def __init__(self, labor, franja, fecha):
        self.labor = labor
        self.franja = franja
        self.fecha = fecha

    def get_labor(self):
        return self.labor

    def get_franja(self):
        return self.franja

    def get_fecha(self):
        return self.fecha


def test_agenda_vacia_al_crearse():
    agenda = Agenda()
    assert agenda.esta_vacia()
    assert agenda.recorrer() == []


def test_agregar_una_sola_asignacion():
    agenda = Agenda()
    a1 = AsignacionFalsa(None, None, date(2026, 1, 10))
    agenda.agregar(a1)
    assert not agenda.esta_vacia()
    assert agenda.get_inicio() == a1
    assert agenda.recorrer() == [a1]


def test_agregar_fuera_de_orden_queda_ordenada_por_fecha(labor_de_prueba):
    labor, franja_manana, _, _ = labor_de_prueba
    agenda = Agenda()
    a_20 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 20))
    a_10 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 10))
    a_15 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 15))

    agenda.agregar(a_20)
    agenda.agregar(a_10)  # llega una anterior a la ya agendada
    agenda.agregar(a_15)  # llega una del medio

    assert agenda.recorrer() == [a_10, a_15, a_20]
    assert agenda.get_inicio() == a_10


def test_agregar_mismo_dia_ordena_por_franja(labor_de_prueba):
    labor, franja_manana, franja_tarde, franja_noche = labor_de_prueba
    agenda = Agenda()
    fecha = date(2026, 1, 10)
    a_noche = AsignacionFalsa(labor, franja_noche, fecha)
    a_manana = AsignacionFalsa(labor, franja_manana, fecha)
    a_tarde = AsignacionFalsa(labor, franja_tarde, fecha)

    agenda.agregar(a_noche)
    agenda.agregar(a_manana)
    agenda.agregar(a_tarde)

    assert agenda.recorrer() == [a_manana, a_tarde, a_noche]


def test_eliminar_del_medio_no_altera_el_resto_del_orden(labor_de_prueba):
    labor, franja_manana, _, _ = labor_de_prueba
    agenda = Agenda()
    a1 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 10))
    a2 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 15))
    a3 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 20))
    agenda.agregar(a1)
    agenda.agregar(a2)
    agenda.agregar(a3)

    agenda.eliminar(a2)

    assert agenda.recorrer() == [a1, a3]


def test_eliminar_el_primero(labor_de_prueba):
    labor, franja_manana, _, _ = labor_de_prueba
    agenda = Agenda()
    a1 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 10))
    a2 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 15))
    agenda.agregar(a1)
    agenda.agregar(a2)

    agenda.eliminar(a1)

    assert agenda.recorrer() == [a2]
    assert agenda.get_inicio() == a2


def test_eliminar_algo_que_no_esta_no_hace_nada(labor_de_prueba):
    labor, franja_manana, _, _ = labor_de_prueba
    agenda = Agenda()
    a1 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 10))
    a2 = AsignacionFalsa(labor, franja_manana, date(2026, 1, 15))
    agenda.agregar(a1)

    agenda.eliminar(a2)

    assert agenda.recorrer() == [a1]


def test_get_inicio_en_agenda_vacia_lanza_index_error():
    agenda = Agenda()
    with pytest.raises(IndexError):
        agenda.get_inicio()
