"""¿Pueden dos registros de alta distintos producir la misma cadena de entrada?

Comprueba lo que afirma la ambigüedad 7 de docs/ambiguedades.md. La cadena no
escapa `&` ni `=`, así que un valor puede imitar el límite entre dos campos.
Estos tests cuentan todas las formas de descomponer una cadena en los ocho
valores de un registro que cumplen unas restricciones dadas: más de una
descomposición significa que dos registros distintos dan la misma cadena y,
por tanto, la misma huella.

Las restricciones del esquema son las de SuministroInformacion.xsd (AEAT),
que no se incluye en el repositorio (ver docs/fuentes/FUENTES.md):

- IDEmisorFactura: NIFType, string de longitud 9, sin pattern.
- NumSerieFactura: TextoIDFacturaType, string de 1 a 60, sin pattern.
- FechaExpedicionFactura: fecha, pattern \\d{2,2}-\\d{2,2}-\\d{4,4}.
- TipoFactura: ClaveTipoFacturaType, enumeración.
- CuotaTotal, ImporteTotal: ImporteSgn12.2Type, pattern (\\+|-)?\\d{1,12}(\\.\\d{0,2})?.
- Huella: TextMax64Type, string de hasta 64, sin pattern.
- FechaHoraHusoGenRegistro: xs:dateTime.

Las longitudes se comprueban sobre el valor ya recortado, que nunca es más
largo que el del XML.
"""

import random
import re

from validador_verifactu.huella import canonicalizar

CAMPOS = [
    "IDEmisorFactura",
    "NumSerieFactura",
    "FechaExpedicionFactura",
    "TipoFactura",
    "CuotaTotal",
    "ImporteTotal",
    "Huella",
    "FechaHoraHusoGenRegistro",
]

FECHA = re.compile(r"\d{2}-\d{2}-\d{4}")
TIPO = re.compile(r"F1|F2|F3|R1|R2|R3|R4|R5")
IMPORTE = re.compile(r"(\+|-)?\d{1,12}(\.\d{0,2})?")
# Forma léxica de xs:dateTime, simplificada: basta con que no admita & ni =.
FECHA_HORA = re.compile(
    r"-?\d{4,}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?"
)


def _libre(maximo):
    return lambda valor: len(valor) <= maximo


def _cerrado(patron):
    return lambda valor: patron.fullmatch(valor) is not None


XSD = [
    _libre(9),
    _libre(60),
    _cerrado(FECHA),
    _cerrado(TIPO),
    _cerrado(IMPORTE),
    _cerrado(IMPORTE),
    _libre(64),
    _cerrado(FECHA_HORA),
]
# Los formatos cerrados del XSD, pero sin límite de longitud en los libres.
XSD_SIN_LONGITUDES = [_libre(10**9), _libre(10**9), *XSD[2:6], _libre(10**9), XSD[7]]
SIN_RESTRICCIONES = [_libre(10**9)] * len(CAMPOS)

# Caso 1 oficial (PDF p. 10), con un NIF de emisor ficticio.
BASE = [
    "00000000T",
    "12345678/G33",
    "01-01-2024",
    "F1",
    "12.35",
    "123.45",
    "3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60",
    "2024-01-01T19:20:30+01:00",
]


def _cadena(valores):
    return canonicalizar(dict(zip(CAMPOS, valores)))


def _cumple(valores, reglas):
    return all(regla(valor) for regla, valor in zip(reglas, valores))


def _descomposiciones(cadena, reglas, limite=10):
    """Tuplas de valores que cumplen `reglas` y producen exactamente `cadena`."""
    resultados = []

    def buscar(k, inicio, valores):
        if len(resultados) >= limite:
            return
        if k == len(CAMPOS) - 1:
            valor = cadena[inicio:]
            if reglas[k](valor):
                resultados.append((*valores, valor))
            return
        separador = f"&{CAMPOS[k + 1]}="
        pos = cadena.find(separador, inicio)
        while pos != -1:
            valor = cadena[inicio:pos]
            if reglas[k](valor):
                buscar(k + 1, pos + len(separador), [*valores, valor])
            pos = cadena.find(separador, pos + 1)

    prefijo = f"{CAMPOS[0]}="
    if cadena.startswith(prefijo):
        buscar(0, len(prefijo), [])
    return resultados


def _con(**cambios):
    valores = list(BASE)
    for campo, valor in cambios.items():
        valores[CAMPOS.index(campo)] = valor
    return valores


def test_la_serializacion_no_es_inyectiva_sin_restricciones():
    # El ejemplo de la ambigüedad 7: la misma cadena desde dos registros.
    a = _con(NumSerieFactura="1&FechaExpedicionFactura=01-01-2024",
             FechaExpedicionFactura="")
    b = _con(NumSerieFactura="1",
             FechaExpedicionFactura="01-01-2024&FechaExpedicionFactura=")

    assert a != b
    assert _cadena(a) == _cadena(b)
    assert len(_descomposiciones(_cadena(a), SIN_RESTRICCIONES)) == 2


def test_el_ejemplo_requiere_valores_que_el_xsd_rechaza():
    a = _con(NumSerieFactura="1&FechaExpedicionFactura=01-01-2024",
             FechaExpedicionFactura="")
    b = _con(NumSerieFactura="1",
             FechaExpedicionFactura="01-01-2024&FechaExpedicionFactura=")

    assert not _cumple(a, XSD)
    assert not _cumple(b, XSD)
    # A además lleva un "=" en NumSerieFactura, que Validaciones 3.1.3.1 prohíbe.
    assert "=" in a[1]


def test_con_ampersand_y_sin_igual_hay_una_sola_descomposicion():
    # "&" (ASCII 38) no está entre los caracteres que Validaciones prohíbe.
    for serie in ["A&B", "&", "A&&B&", "&FechaExpedicionFactura",
                  "X&TipoFactura&Huella&"]:
        valores = _con(NumSerieFactura=serie)
        assert len(_descomposiciones(_cadena(valores), XSD)) == 1, serie


def test_con_el_xsd_no_hay_colisiones_aunque_haya_ampersand_e_igual():
    # Valores aleatorios en los tres campos libres, hechos de trozos de
    # separadores y de valores válidos para provocar límites falsos, dentro de
    # las longitudes del XSD. Semilla fija: el resultado es reproducible.
    trozos = [f"&{campo}=" for campo in CAMPOS] + [
        "01-01-2024", "F1", "1", "12.35", "2024-01-01T19:20:30+01:00", "A", "=", "&",
    ]
    azar = random.Random(0)

    def libre_aleatorio(maximo):
        partes = (azar.choice(trozos) for _ in range(azar.randint(0, 12)))
        return "".join(partes)[:maximo]

    for _ in range(20000):
        valores = _con(
            IDEmisorFactura=libre_aleatorio(9),
            NumSerieFactura=libre_aleatorio(60) or "A",
            Huella=libre_aleatorio(64),
        )
        assert len(_descomposiciones(_cadena(valores), XSD)) == 1, valores


def test_sin_los_limites_de_longitud_la_colision_se_puede_construir():
    # Entre NumSerieFactura y Huella hay cuatro campos cerrados: para imitar
    # ese tramo hay que meterlo entero dentro de uno de los dos campos libres.
    tramo = ("&FechaExpedicionFactura=02-02-2024&TipoFactura=F2"
             "&CuotaTotal=1&ImporteTotal=1&Huella=")
    assert len(tramo) == 85

    c = _con(NumSerieFactura="A" + tramo + "X")
    d = _con(
        NumSerieFactura="A",
        FechaExpedicionFactura="02-02-2024",
        TipoFactura="F2",
        CuotaTotal="1",
        ImporteTotal="1",
        Huella=(f"X&FechaExpedicionFactura={BASE[2]}&TipoFactura={BASE[3]}"
                f"&CuotaTotal={BASE[4]}&ImporteTotal={BASE[5]}&Huella={BASE[6]}"),
    )

    assert _cadena(c) == _cadena(d)
    assert _cumple(c, XSD_SIN_LONGITUDES) and _cumple(d, XSD_SIN_LONGITUDES)
    assert len(_descomposiciones(_cadena(c), XSD_SIN_LONGITUDES)) == 2
    # Con las longitudes del XSD, ninguno de los dos registros es válido.
    assert len(c[1]) > 60 and len(d[6]) > 64
    assert not _cumple(c, XSD) and not _cumple(d, XSD)
