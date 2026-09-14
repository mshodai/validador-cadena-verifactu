"""Vectores oficiales de registros de alta.

Fuente: docs/fuentes/Veri-Factu_especificaciones_huella_hash_registros.pdf
(AEAT, v0.1.2), transcritos en docs/campos-huella-alta.md, sección 6.
"""

from validador_verifactu.huella import calcular_huella, canonicalizar

REGISTRO_CASO_1 = {
    "IDEmisorFactura": "89890001K",
    "NumSerieFactura": "12345678/G33",
    "FechaExpedicionFactura": "01-01-2024",
    "TipoFactura": "F1",
    "CuotaTotal": "12.35",
    "ImporteTotal": "123.45",
    "Huella": "",
    "FechaHoraHusoGenRegistro": "2024-01-01T19:20:30+01:00",
}
CADENA_CASO_1 = (
    "IDEmisorFactura=89890001K&NumSerieFactura=12345678/G33"
    "&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35"
    "&ImporteTotal=123.45&Huella="
    "&FechaHoraHusoGenRegistro=2024-01-01T19:20:30+01:00"
)
HUELLA_CASO_1 = "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60"

REGISTRO_CASO_2 = {
    "IDEmisorFactura": "89890001K",
    "NumSerieFactura": "12345679/G34",
    "FechaExpedicionFactura": "01-01-2024",
    "TipoFactura": "F1",
    "CuotaTotal": "12.35",
    "ImporteTotal": "123.45",
    "Huella": "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60",
    "FechaHoraHusoGenRegistro": "2024-01-01T19:20:35+01:00",
}
CADENA_CASO_2 = (
    "IDEmisorFactura=89890001K&NumSerieFactura=12345679/G34"
    "&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35"
    "&ImporteTotal=123.45"
    "&Huella=3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60"
    "&FechaHoraHusoGenRegistro=2024-01-01T19:20:35+01:00"
)
HUELLA_CASO_2 = "F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97"


def test_canonicalizar_caso_1():
    """Caso 1, primer registro de alta sin huella anterior (PDF p. 10)."""
    assert canonicalizar(REGISTRO_CASO_1) == CADENA_CASO_1


def test_calcular_huella_caso_1():
    """Caso 1, primer registro de alta sin huella anterior (PDF p. 10)."""
    assert calcular_huella(CADENA_CASO_1) == HUELLA_CASO_1


def test_canonicalizar_caso_2():
    """Caso 2, registro de alta encadenado al caso 1 (PDF p. 11)."""
    assert canonicalizar(REGISTRO_CASO_2) == CADENA_CASO_2


def test_calcular_huella_caso_2():
    """Caso 2, registro de alta encadenado al caso 1 (PDF p. 11)."""
    assert calcular_huella(CADENA_CASO_2) == HUELLA_CASO_2
