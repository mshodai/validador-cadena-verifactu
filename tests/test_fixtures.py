"""Los corpus sintéticos de fixtures/ dan el resultado que documentan."""

import json
from pathlib import Path

from validador_verifactu.cadena import validar_cadena

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _validar(nombre):
    with open(FIXTURES / nombre, encoding="utf-8") as f:
        return [(i["codigo"], i["posicion"]) for i in validar_cadena(json.load(f))]


def test_cadena_valida():
    assert _validar("cadena-valida.json") == []


def test_cadena_rota():
    assert _validar("cadena-rota.json") == [("E01", 4), ("E02", 8)]
