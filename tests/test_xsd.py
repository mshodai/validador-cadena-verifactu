"""Normalización de los valores según su tipo en el esquema XSD.

FechaHoraHusoGenRegistro es xs:dateTime (whiteSpace="collapse"); los otros
siete campos que entran en la huella derivan de xs:string ("preserve").
"""

from test_cadena import CASO_1, CASO_2
from validador_verifactu.cadena import validar_cadena
from validador_verifactu.huella import calcular_huella, canonicalizar
from validador_verifactu.xsd import normalizar_segun_xsd

FECHA = CASO_1["FechaHoraHusoGenRegistro"]
# Texto literal del elemento en un XML indentado.
FECHA_INDENTADA = f"\n    {FECHA}\n  "


def test_la_fecha_indentada_se_colapsa():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": FECHA_INDENTADA}

    assert normalizar_segun_xsd(registro)["FechaHoraHusoGenRegistro"] == FECHA


def test_la_fecha_indentada_da_la_misma_huella_que_sin_indentar():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": FECHA_INDENTADA}

    normalizado = normalizar_segun_xsd(registro)

    assert calcular_huella(canonicalizar(normalizado)) == CASO_1["HuellaPropia"]


def test_un_registro_conforme_con_xml_indentado_no_da_e01():
    indentado = {**CASO_1, "FechaHoraHusoGenRegistro": FECHA_INDENTADA}

    assert validar_cadena([indentado, CASO_2]) == []


def test_se_colapsan_tabuladores_y_retornos_de_carro():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": f"\t\r\n {FECHA} \t"}

    assert normalizar_segun_xsd(registro)["FechaHoraHusoGenRegistro"] == FECHA


def test_las_secuencias_interiores_se_reducen_a_un_espacio():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": "a \t\n b"}

    assert normalizar_segun_xsd(registro)["FechaHoraHusoGenRegistro"] == "a b"


def test_el_espacio_de_no_separacion_no_se_elimina():
    # U+00A0 no es espacio en blanco para XML Schema.
    valor = f"\u00a0{FECHA}\u00a0"
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": valor}

    assert normalizar_segun_xsd(registro)["FechaHoraHusoGenRegistro"] == valor


def test_es_idempotente():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": FECHA_INDENTADA}

    una_vez = normalizar_segun_xsd(registro)

    assert normalizar_segun_xsd(una_vez) == una_vez
    assert normalizar_segun_xsd(CASO_1) == CASO_1


def test_los_otros_siete_campos_no_se_tocan():
    # Derivan de xs:string: el espacio en blanco forma parte del valor.
    registro = {
        campo: f"\n {valor}\t"
        for campo, valor in CASO_1.items()
        if campo not in ("FechaHoraHusoGenRegistro", "HuellaPropia")
    }
    registro["FechaHoraHusoGenRegistro"] = FECHA

    assert normalizar_segun_xsd(registro) == registro


def test_no_modifica_el_diccionario_de_entrada():
    registro = {**CASO_1, "FechaHoraHusoGenRegistro": FECHA_INDENTADA}

    normalizar_segun_xsd(registro)

    assert registro["FechaHoraHusoGenRegistro"] == FECHA_INDENTADA


def test_un_campo_ausente_o_nulo_se_deja_como_esta():
    sin_fecha = {k: v for k, v in CASO_1.items() if k != "FechaHoraHusoGenRegistro"}
    con_nulo = {**CASO_1, "FechaHoraHusoGenRegistro": None}

    assert normalizar_segun_xsd(sin_fecha) == sin_fecha
    assert normalizar_segun_xsd(con_nulo) == con_nulo
