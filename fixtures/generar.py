"""Genera fixtures/cadena-valida.json y fixtures/cadena-rota.json.

Uso, desde cualquier directorio: python fixtures/generar.py

Los datos son sintéticos y deterministas: cada ejecución produce exactamente
los mismos ficheros. Las huellas se calculan con el código de src/, así que hay
que volver a ejecutar el script si cambia canonicalizar o calcular_huella.
"""

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent
# Usa siempre el código de src/, no una versión instalada del paquete.
sys.path.insert(0, str(DIRECTORIO.parent / "src"))

from validador_verifactu.cadena import validar_cadena  # noqa: E402
from validador_verifactu.huella import calcular_huella, canonicalizar  # noqa: E402

# NIF ficticio: ocho ceros con su letra de control.
NIF_FICTICIO = "00000000T"
NUM_REGISTROS = 12
# Posiciones tal como las informa el validador, empezando en 0.
POSICION_E01 = 4
POSICION_E02 = 8


def facturas():
    """Campos de las facturas, sin huellas: una factura F1 al día desde el
    2 de enero de 2025, con IVA del 21 % y el registro generado ese mismo día."""
    registros = []
    for i in range(NUM_REGISTROS):
        dia = i + 2
        base = Decimal("100.00") + Decimal("37.25") * i
        cuota = (base * Decimal("0.21")).quantize(Decimal("0.01"), ROUND_HALF_UP)
        registros.append({
            "IDEmisorFactura": NIF_FICTICIO,
            "NumSerieFactura": f"PRUEBA-2025-{i + 1:04d}",
            "FechaExpedicionFactura": f"{dia:02d}-01-2025",
            "TipoFactura": "F1",
            "CuotaTotal": str(cuota),
            "ImporteTotal": str(base + cuota),
            "Huella": "",
            "FechaHoraHusoGenRegistro": f"2025-01-{dia:02d}T10:00:00+01:00",
        })
    return registros


def encadenar(registros, anterior_de=None):
    """Rellena Huella y HuellaPropia en orden. `anterior_de` indica, para
    alguna posición, a qué registro enlazar en lugar del inmediatamente
    anterior."""
    anterior_de = anterior_de or {}
    for posicion, registro in enumerate(registros):
        anterior = anterior_de.get(posicion, posicion - 1)
        registro["Huella"] = registros[anterior]["HuellaPropia"] if anterior >= 0 else ""
        registro["HuellaPropia"] = calcular_huella(canonicalizar(registro))
    return registros


def main():
    valida = encadenar(facturas())

    # E02: el registro POSICION_E02 enlaza con la huella de dos registros atrás
    # en lugar de con la del anterior. Su huella y las de los siguientes se
    # calculan con ese enlace, así que la cadena solo se rompe en ese punto.
    rota = encadenar(facturas(), anterior_de={POSICION_E02: POSICION_E02 - 2})
    # E01: el importe del registro POSICION_E01 se altera después de calcular
    # su huella.
    alterado = rota[POSICION_E01]
    alterado["ImporteTotal"] = str(Decimal(alterado["ImporteTotal"]) + Decimal("100.00"))

    ficheros = (
        ("cadena-valida.json", valida, []),
        ("cadena-rota.json", rota, [("E01", POSICION_E01), ("E02", POSICION_E02)]),
    )
    for nombre, registros, esperadas in ficheros:
        obtenidas = [(i["codigo"], i["posicion"]) for i in validar_cadena(registros)]
        if obtenidas != esperadas:
            sys.exit(f"{nombre}: se esperaban {esperadas} y se obtuvieron {obtenidas}")
    for nombre, registros, _ in ficheros:
        with open(DIRECTORIO / nombre, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(registros, ensure_ascii=False, indent=2) + "\n")
        print(f"Escrito fixtures/{nombre}")


if __name__ == "__main__":
    main()
