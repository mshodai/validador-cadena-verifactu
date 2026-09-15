from validador_verifactu.huella import calcular_huella, canonicalizar
from validador_verifactu.xsd import normalizar_segun_xsd


def validar_cadena(registros: list[dict]) -> list[dict]:
    """Incidencias E01 y E02 de una secuencia ordenada de registros de alta.

    Cada registro es el diccionario que acepta `canonicalizar`, más la clave
    "HuellaPropia" con la huella que declaró el emisor (RegistroAlta/Huella).
    Los valores pueden ser el texto literal de cada elemento XML: antes de
    calcular la huella se normalizan según su tipo en el esquema XSD.
    El primer elemento de `registros` se trata como el primer registro del
    sistema.

    Cada incidencia es un diccionario con "codigo", "posicion" (índice del
    registro en `registros`, empezando en 0) y "mensaje".
    """
    registros = [normalizar_segun_xsd(registro) for registro in registros]
    incidencias = []
    huella_anterior = ""
    for posicion, registro in enumerate(registros):
        # AMBIGÜEDAD: las huellas se comparan como texto exacto. La
        # especificación define el recorte de espacios solo para montar la
        # cadena (p. 6), no para comparar huellas entre registros.
        declarada = registro.get("HuellaPropia") or ""
        encadenada = registro.get("Huella") or ""

        recalculada = calcular_huella(canonicalizar(registro))
        if declarada != recalculada:
            incidencias.append({
                "codigo": "E01",
                "posicion": posicion,
                "mensaje": (
                    "La huella declarada no coincide con la recalculada a partir "
                    f"de los campos: se esperaba {recalculada}, se encontró "
                    f"{declarada or '(vacío)'}."
                ),
            })

        if encadenada != huella_anterior:
            if posicion == 0:
                motivo = "El primer registro debe llevar el campo Huella vacío"
            else:
                motivo = (
                    "El campo Huella no coincide con la HuellaPropia del "
                    "registro anterior"
                )
            incidencias.append({
                "codigo": "E02",
                "posicion": posicion,
                "mensaje": (
                    f"{motivo}: se esperaba {huella_anterior or '(vacío)'}, "
                    f"se encontró {encadenada or '(vacío)'}."
                ),
            })

        # Se encadena con la huella declarada, no con la recalculada: un E01 en
        # este registro no provoca un E02 en el siguiente.
        huella_anterior = declarada
    return incidencias
