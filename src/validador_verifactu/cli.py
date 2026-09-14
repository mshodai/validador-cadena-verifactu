"""Línea de órdenes: validar-verifactu FICHERO [--json]."""

import argparse
import json
import sys

from validador_verifactu.cadena import validar_cadena


class _Formato(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix or "uso: ")


def main(argv=None) -> int:
    """Devuelve 0 si la cadena está íntegra, 1 si hay incidencias y 2 si el
    fichero no se puede leer o no tiene el formato esperado."""
    parser = argparse.ArgumentParser(
        prog="validar-verifactu",
        description=(
            "Valida la huella y el encadenamiento de una secuencia ordenada de "
            "registros de alta de VeriFactu."
        ),
        formatter_class=_Formato,
        add_help=False,
    )
    argumentos = parser.add_argument_group("argumentos")
    argumentos.add_argument(
        "fichero", help="fichero JSON con la lista ordenada de registros de alta"
    )
    opciones = parser.add_argument_group("opciones")
    opciones.add_argument(
        "-h", "--help", action="help", help="muestra esta ayuda y termina"
    )
    opciones.add_argument(
        "--json",
        action="store_true",
        help="emite el resultado en JSON en lugar de texto",
    )
    args = parser.parse_args(argv)

    try:
        registros = _leer_registros(args.fichero)
    except ValueError as e:
        print(f"{parser.prog}: error: {e}", file=sys.stderr)
        return 2

    incidencias = validar_cadena(registros)
    if args.json:
        print(json.dumps(incidencias, ensure_ascii=False, indent=2))
    elif incidencias:
        for incidencia in incidencias:
            print(
                f"{incidencia['codigo']} en la posición {incidencia['posicion']}: "
                f"{incidencia['mensaje']}"
            )
    else:
        n = len(registros)
        print(
            f"Cadena íntegra: {n} {'registro' if n == 1 else 'registros'} "
            "sin incidencias."
        )
    return 1 if incidencias else 0


def _leer_registros(ruta):
    """Lista de registros del fichero. Lanza ValueError con el motivo si no se
    puede leer o no es una lista de objetos con valores de texto o null."""
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"no existe el fichero {ruta}") from None
    except OSError as e:
        raise ValueError(f"no se puede leer el fichero {ruta}: {e.strerror}") from None
    except UnicodeDecodeError:
        raise ValueError(f"el fichero {ruta} no está codificado en UTF-8") from None
    except json.JSONDecodeError as e:
        raise ValueError(
            f"el fichero {ruta} no es JSON válido (línea {e.lineno}, columna {e.colno})"
        ) from None

    if not isinstance(datos, list):
        raise ValueError("el JSON debe ser una lista de registros")
    for posicion, registro in enumerate(datos):
        if not isinstance(registro, dict):
            raise ValueError(f"el registro en la posición {posicion} no es un objeto JSON")
        for campo, valor in registro.items():
            if valor is not None and not isinstance(valor, str):
                raise ValueError(
                    f"el campo {campo} del registro en la posición {posicion} "
                    "debe ser texto o null"
                )
    return datos


if __name__ == "__main__":
    sys.exit(main())
