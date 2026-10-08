from datetime import date


class CredencialProfesional:

    def __init__(self, nombre, fecha_obtencion, fecha_caducidad):
        if not isinstance(nombre, str):
            raise TypeError("nombre debe ser un string")
        if nombre.strip() == "":
            raise ValueError("nombre no puede estar vacio")
        if not isinstance(fecha_obtencion, date):
            raise TypeError("fecha_obtencion debe ser un date")
        if not isinstance(fecha_caducidad, date):
            raise TypeError("fecha_caducidad debe ser un date")
        if fecha_caducidad <= fecha_obtencion:
            raise ValueError("La fecha de caducidad debe ser posterior a la fecha de obtencion")

        self._nombre = nombre
        self._fecha_obtencion = fecha_obtencion
        self._fecha_caducidad = fecha_caducidad

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_fecha_obtencion(self):
        return self._fecha_obtencion

    def set_fecha_obtencion(self, fecha_obtencion):
        self._fecha_obtencion = fecha_obtencion

    def get_fecha_caducidad(self):
        return self._fecha_caducidad

    def set_fecha_caducidad(self, fecha_caducidad):
        self._fecha_caducidad = fecha_caducidad

    def esta_activa(self, fecha_referencia):
        return self._fecha_obtencion <= fecha_referencia <= self._fecha_caducidad


def test_credencial_invalida_lanza_value_error():
    import pytest

    with pytest.raises(ValueError):
        CredencialProfesional("Certificado", date(2025, 1, 1), date(2024, 1, 1))


def test_credencial_tipos_invalidos_lanza_type_error():
    import pytest

    with pytest.raises(TypeError):
        CredencialProfesional(123, date(2025, 1, 1), date(2026, 1, 1))
    with pytest.raises(TypeError):
        CredencialProfesional("Certificado", "2025-01-01", date(2026, 1, 1))


def test_credencial_nombre_vacio_lanza_value_error():
    import pytest

    with pytest.raises(ValueError):
        CredencialProfesional("   ", date(2025, 1, 1), date(2026, 1, 1))


def test_credencial_esta_activa_dentro_del_rango():
    credencial = CredencialProfesional("Certificado", date(2025, 1, 1), date(2026, 1, 1))
    assert credencial.esta_activa(date(2025, 6, 1))


def test_credencial_no_esta_activa_fuera_del_rango():
    credencial = CredencialProfesional("Certificado", date(2025, 1, 1), date(2026, 1, 1))
    assert not credencial.esta_activa(date(2027, 1, 1))
