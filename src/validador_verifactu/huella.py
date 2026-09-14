import hashlib


def calcular_huella(cadena: str) -> str:
    """SHA-256 de la cadena codificada en UTF-8, en hexadecimal y mayúsculas."""
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest().upper()
