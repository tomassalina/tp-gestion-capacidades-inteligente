from tipo_accion_bitacora import TipoAccionBitacora


def test_las_tres_acciones_son_distintas_entre_si():
    acciones = {TipoAccionBitacora.PROPUESTA, TipoAccionBitacora.APROBACION, TipoAccionBitacora.REVERSION}
    assert len(acciones) == 3
