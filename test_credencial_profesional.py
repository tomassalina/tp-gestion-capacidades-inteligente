from datetime import date

import pytest

from credencial_profesional import CredencialProfesional


def test_credencial_invalida_lanza_value_error():
    with pytest.raises(ValueError):
        CredencialProfesional("Certificado", date(2025, 1, 1), date(2024, 1, 1))


def test_credencial_tipos_invalidos_lanza_type_error():
    with pytest.raises(TypeError):
        CredencialProfesional(123, date(2025, 1, 1), date(2026, 1, 1))
    with pytest.raises(TypeError):
        CredencialProfesional("Certificado", "2025-01-01", date(2026, 1, 1))


def test_credencial_nombre_vacio_lanza_value_error():
    with pytest.raises(ValueError):
        CredencialProfesional("   ", date(2025, 1, 1), date(2026, 1, 1))


def test_credencial_esta_activa_dentro_del_rango():
    credencial = CredencialProfesional("Certificado", date(2025, 1, 1), date(2026, 1, 1))
    assert credencial.esta_activa(date(2025, 6, 1))


def test_credencial_no_esta_activa_fuera_del_rango():
    credencial = CredencialProfesional("Certificado", date(2025, 1, 1), date(2026, 1, 1))
    assert not credencial.esta_activa(date(2027, 1, 1))
