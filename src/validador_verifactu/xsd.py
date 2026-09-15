import re

# Espacio en blanco según XML Schema: solo estos cuatro caracteres. No incluye
# U+00A0 ni otros espacios Unicode, que str.split() y str.strip() sí tratarían
# como espacio.
_ESPACIO_XSD = re.compile(r"[ \t\n\r]+")


def normalizar_segun_xsd(registro: dict) -> dict:
    """Copia de `registro` con los valores tal como los normaliza el esquema XSD.

    Los valores pueden venir como el texto literal del elemento XML (con saltos
    de línea y sangría si el XML está indentado) o ya normalizados. La
    normalización es idempotente, así que da el mismo resultado en ambos casos.
    """
    # DECISIÓN (ambigüedad 6, resuelta para este campo): en
    # SuministroInformacion.xsd, FechaHoraHusoGenRegistro es xs:dateTime, cuya
    # faceta whiteSpace es "collapse" y no se puede cambiar (XML Schema 1.0,
    # parte 2, §3.2.7 y §4.3.6). "La misma información contenida en el campo"
    # (p. 6) es, por tanto, el valor colapsado, no el texto literal. Los otros
    # siete campos derivan de xs:string, cuya faceta es "preserve": su texto es
    # su valor y no se tocan.
    valor = registro.get("FechaHoraHusoGenRegistro")
    if not isinstance(valor, str):
        return dict(registro)
    return {**registro, "FechaHoraHusoGenRegistro": _colapsar(valor)}


def _colapsar(valor: str) -> str:
    """whiteSpace="collapse": cada secuencia de espacio en blanco XSD se
    sustituye por un espacio y se eliminan los del principio y el final."""
    return _ESPACIO_XSD.sub(" ", valor).strip(" ")
