"""Línea de órdenes validar-verifactu, con los registros de test_cadena."""

import json

from test_cadena import CASO_1, CASO_2, CASO_2_ALTERADO, CASO_3
from validador_verifactu.cadena import validar_cadena
from validador_verifactu.cli import main


def _escribir(tmp_path, registros):
    ruta = tmp_path / "registros.json"
    ruta.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")
    return str(ruta)


def test_cadena_valida_devuelve_0(tmp_path):
    assert main([_escribir(tmp_path, [CASO_1, CASO_2, CASO_3])]) == 0


def test_cadena_con_incidencias_devuelve_1(tmp_path):
    assert main([_escribir(tmp_path, [CASO_1, CASO_2_ALTERADO, CASO_3])]) == 1


def test_fichero_inexistente_devuelve_2(tmp_path):
    assert main([str(tmp_path / "no-existe.json")]) == 2


def test_json_invalido_devuelve_2(tmp_path):
    ruta = tmp_path / "roto.json"
    ruta.write_text('[{"IDEmisorFactura": ', encoding="utf-8")

    assert main([str(ruta)]) == 2


def test_opcion_json_emite_json_parseable(tmp_path, capsys):
    registros = [CASO_1, CASO_2_ALTERADO, CASO_3]

    codigo = main(["--json", _escribir(tmp_path, registros)])

    assert codigo == 1
    assert json.loads(capsys.readouterr().out) == validar_cadena(registros)
