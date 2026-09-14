import hashlib


def calcular_huella(cadena: str) -> str:
    """SHA-256 de la cadena codificada en UTF-8, en hexadecimal y mayúsculas."""
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest().upper()


def canonicalizar(registro: dict) -> str:
    """Cadena de entrada de la huella de un registro de alta.

    `registro` asocia el nombre de cada campo con su valor en el XML. La clave
    "Huella" es la huella del registro anterior
    (Encadenamiento/RegistroAnterior/Huella), no la del propio registro.
    Un campo ausente o con valor None se trata como vacío.
    """
    # Orden de la p. 5 (docs/campos-huella-alta.md, sección 1).
    # AMBIGÜEDAD: la p. 5 dice que este orden coincide con el de los diseños de
    # registro del anexo de la orden, que no está disponible. Se usa el orden
    # enunciado en la p. 5 sin haberlo comprobado contra el anexo.
    campos = (
        "IDEmisorFactura",
        "NumSerieFactura",
        "FechaExpedicionFactura",
        "TipoFactura",
        "CuotaTotal",
        "ImporteTotal",
        "Huella",
        "FechaHoraHusoGenRegistro",
    )
    pares = []
    for nombre in campos:
        valor = registro.get(nombre)
        if valor is None:
            valor = ""
        # AMBIGÜEDAD: la p. 6 manda quitar "los espacios al inicio y al final",
        # pero no dice si cuentan como espacio los tabuladores, los saltos de
        # línea, el espacio de no separación u otros blancos. El trim() del
        # ejemplo Java (p. 8) también quita caracteres de control. Aquí solo se
        # quita el espacio U+0020.
        valor = valor.strip(" ")
        # AMBIGÜEDAD: según la p. 6, el valor es "la misma información" del XML,
        # pero no aclara si las referencias de entidad (&amp;) van resueltas, si
        # se normaliza Unicode ni si FechaExpedicionFactura se reformatea (el
        # ejemplo Java de la p. 8 la pasa por un formatea() sin definir). El
        # valor se usa tal como llega.
        # AMBIGÜEDAD: en los campos numéricos, "123.1" y "123.10" "se tratarán
        # indistintamente" (p. 6), pero no se dice qué texto va en la cadena, qué
        # campos son numéricos ni cómo tratar los valores sin decimales. El
        # valor no se normaliza.
        # AMBIGÜEDAD: no se dice qué hacer si el valor contiene "&" o "=". El
        # ejemplo Java define una codificación URL que nunca llega a usar. El
        # valor no se codifica.
        pares.append(f"{nombre}={valor}")
    return "&".join(pares)
