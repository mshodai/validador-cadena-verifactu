"""Validación de cadenas de registros de alta.

CASO_1 y CASO_2 son los vectores oficiales de los casos 1 (PDF p. 10) y 2
(PDF p. 11), con la huella esperada como HuellaPropia. CASO_3 y CASO_4 no
están en el documento: se derivan del caso 2 cambiando el número de serie y la
fecha de generación, y su huella se calcula con calcular_huella.
"""

from test_huella import (
    HUELLA_CASO_1,
    HUELLA_CASO_2,
    REGISTRO_CASO_1,
    REGISTRO_CASO_2,
)
from validador_verifactu.cadena import validar_cadena
from validador_verifactu.huella import calcular_huella, canonicalizar


def _siguiente(anterior, num_serie, fecha_hora):
    """Registro de alta encadenado a `anterior`, con su huella calculada."""
    registro = {
        **anterior,
        "NumSerieFactura": num_serie,
        "Huella": anterior["HuellaPropia"],
        "FechaHoraHusoGenRegistro": fecha_hora,
    }
    registro["HuellaPropia"] = calcular_huella(canonicalizar(registro))
    return registro


CASO_1 = {**REGISTRO_CASO_1, "HuellaPropia": HUELLA_CASO_1}
CASO_2 = {**REGISTRO_CASO_2, "HuellaPropia": HUELLA_CASO_2}
CASO_3 = _siguiente(CASO_2, "12345680/G35", "2024-01-01T19:20:40+01:00")
CASO_4 = _siguiente(CASO_3, "12345681/G36", "2024-01-01T19:20:45+01:00")

# Caso 2 con un importe alterado y la huella original: ya no le corresponde.
CASO_2_ALTERADO = {**CASO_2, "ImporteTotal": "123.46"}


def _codigos(incidencias):
    return [(i["codigo"], i["posicion"]) for i in incidencias]


def test_cadena_valida():
    assert validar_cadena([CASO_1, CASO_2, CASO_3]) == []


def test_e01_en_medio():
    incidencias = validar_cadena([CASO_1, CASO_2_ALTERADO, CASO_3])

    assert _codigos(incidencias) == [("E01", 1)]
    recalculada = calcular_huella(canonicalizar(CASO_2_ALTERADO))
    assert f"se esperaba {recalculada}" in incidencias[0]["mensaje"]
    assert f"se encontró {HUELLA_CASO_2}" in incidencias[0]["mensaje"]


def test_e02_en_medio():
    # Falta el caso 2: el caso 3 apunta a su huella, no a la del caso 1.
    incidencias = validar_cadena([CASO_1, CASO_3, CASO_4])

    assert _codigos(incidencias) == [("E02", 1)]
    assert f"se esperaba {HUELLA_CASO_1}" in incidencias[0]["mensaje"]
    assert f"se encontró {HUELLA_CASO_2}" in incidencias[0]["mensaje"]


def test_e02_primer_registro_con_huella():
    # El caso 2 lleva la huella del caso 1; como primer registro debería ir vacía.
    incidencias = validar_cadena([CASO_2, CASO_3])

    assert _codigos(incidencias) == [("E02", 0)]
    assert "se esperaba (vacío)" in incidencias[0]["mensaje"]
    assert f"se encontró {HUELLA_CASO_1}" in incidencias[0]["mensaje"]


def test_sigue_evaluando_tras_un_fallo():
    # E01 en la posición 1 y, después, un E02 en la posición 2 porque el caso 4
    # apunta al caso 3, que no está en la secuencia.
    incidencias = validar_cadena([CASO_1, CASO_2_ALTERADO, CASO_4])

    assert _codigos(incidencias) == [("E01", 1), ("E02", 2)]
