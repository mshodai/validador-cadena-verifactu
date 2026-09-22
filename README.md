# validador-cadena-verifactu

Si conservas tus propios registros de facturación y te los requiere Hacienda,
tienes que enviarlos tal como se generaron. Esta herramienta comprueba antes que
la cadena está intacta: que la huella de cada registro cuadra con sus datos y
que ninguno se ha perdido ni alterado por el camino.

Artículos:

- [¿Pueden dos facturas distintas tener la misma huella?](https://mshodai.github.io/validador-cadena-verifactu/),
  sobre por qué la concatenación de la huella no colisiona con registros válidos.
- [¿Basta la especificación de la huella para implementarla?](https://mshodai.github.io/validador-cadena-verifactu/el-esquema-decide.html),
  sobre las decisiones que no toma la especificación y fija el esquema XSD.
- [¿Qué comprueba Hacienda al recibir tus registros en un requerimiento?](https://mshodai.github.io/validador-cadena-verifactu/que-comprueba-hacienda.html),
  sobre qué valida la AEAT y qué no figura entre sus validaciones documentadas.

## El escenario

Es el caso de un sistema informático de facturación (SIF) que no funciona en
modalidad VERI\*FACTU: no envía los registros a la AEAT a medida que los genera,
sino que los conserva él mismo. Cada registro incluye la huella del anterior,
así que forman una cadena, y un registro alterado, perdido, añadido o fuera de
orden la rompe en ese punto. Para detectarlo, la herramienta recalcula cada
huella según la especificación de la AEAT y recorre la cadena de principio a
fin.

## Ejecútalo en 60 segundos

Hace falta Python 3 (probado con Python 3.14). No tiene dependencias externas;
`pip install` solo descarga setuptools para construir el paquete. Desde la raíz
del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install .
```

El repositorio incluye dos corpus sintéticos en `fixtures/`, de 12 registros
cada uno. El primero es una cadena válida:

```
$ validar-verifactu fixtures/cadena-valida.json
Cadena íntegra: 12 registros sin incidencias.
```

El segundo es la misma cadena con dos roturas deliberadas: el importe del
registro en la posición 4 se alteró después de calcular su huella, y el
registro en la posición 8 enlaza con el registro 6 en lugar del 7. El resto de
registros es válido, y el validador sigue evaluándolos después de cada fallo:

```
$ validar-verifactu fixtures/cadena-rota.json
E01 en la posición 4: La huella declarada no coincide con la recalculada a partir de los campos: se esperaba 664E22450AB08A0C5C95074A67C1B8D1D99B39BBF66486F2DDAD66B01BC7D432, se encontró 26D4B49C33730AD38CBE7613E3B9075CC0CE14D49299DDDC71DC129C7BFEDC85.
E02 en la posición 8: El campo Huella no coincide con la HuellaPropia del registro anterior: se esperaba A1BC548705F78BFB1791590687969A692F28A3611A4CBD46C39BA334F2B82F2A, se encontró D809BEE2761463FDBC8C306EBB30D50D7DA493A7FA015037AC88C3EF2F0EC813.
```

Las posiciones empiezan en 0. El código de salida es 0 si la cadena está
íntegra, 1 si hay incidencias y 2 si el fichero no se puede leer o no tiene el
formato esperado. Con `--json`, el resultado se emite como una lista JSON de
incidencias, cada una con `codigo`, `posicion` y `mensaje`.

Los corpus se regeneran con `python fixtures/generar.py`.

### Con tus propios registros

La entrada es un fichero JSON con la lista ordenada de registros de alta. Cada
registro lleva los ocho campos que entran en la huella, con el valor tal como
aparece en el XML, y `HuellaPropia`, la huella que el sistema declaró para ese
registro:

```json
{
  "IDEmisorFactura": "00000000T",
  "NumSerieFactura": "PRUEBA-2025-0001",
  "FechaExpedicionFactura": "02-01-2025",
  "TipoFactura": "F1",
  "CuotaTotal": "21.00",
  "ImporteTotal": "121.00",
  "Huella": "",
  "FechaHoraHusoGenRegistro": "2025-01-02T10:00:00+01:00",
  "HuellaPropia": "BD728770E9C27E105AB1F144D5729D0D02290F5472A47BC41A7AB0673586F343"
}
```

`Huella` es la huella del registro anterior
(`Encadenamiento/RegistroAnterior/Huella`); `HuellaPropia` es la del propio
registro (`RegistroAlta/Huella`). Todos los valores deben ser cadenas de texto,
incluidos los importes: como número JSON, `121.00` se leería como `121.0` y la
huella cambiaría. Un campo ausente o `null` se trata como vacío.

Cada valor puede ser el texto literal del elemento XML o el valor ya
normalizado por el esquema. En `FechaHoraHusoGenRegistro`, que en el esquema XSD
es `xs:dateTime`, el validador elimina antes el espacio en blanco que el esquema
colapsa (espacio, tabulador, salto de línea y retorno de carro), así que un XML
indentado da el mismo resultado. En los demás campos, el texto se usa tal cual.

## Qué comprueba

Dos reglas, en cada registro de la secuencia:

- **E01: la huella declarada no corresponde a los datos.** Se monta la cadena
  de entrada con los ocho campos del registro, en el orden y el formato de la
  especificación, se calcula su SHA-256 y se compara con `HuellaPropia`. Si no
  coinciden, el registro se modificó después de generarse o su huella se
  calculó de otra manera.
- **E02: el registro no enlaza con el anterior.** El campo `Huella` de cada
  registro debe ser igual a la `HuellaPropia` del registro precedente; en el
  primero, debe estar vacío. Si no, falta un registro, sobra uno, están
  desordenados o la cadena se rompió en ese punto.

E02 compara con la huella *declarada* del registro anterior, no con la
recalculada. Así, un registro alterado da E01 en sí mismo, pero no arrastra
incidencias a los siguientes. La secuencia se recorre entera y se informan todas
las incidencias, no solo la primera.

## Qué no hace

- Solo trata registros de alta. No valida registros de anulación ni de evento.
- No lee XML. Espera los valores ya extraídos a JSON; cómo se extraen del XML
  (espacios, referencias de entidad, normalización Unicode) queda fuera y puede
  cambiar la huella.
- No valida el contenido fiscal: ni NIF, ni importes, ni tipos de factura, ni
  fechas.
- No emite facturas ni genera registros.
- No firma registros ni comprueba firmas electrónicas.
- No se conecta a la AEAT ni remite nada.

El encadenamiento por sí solo no detecta una cadena reescrita por completo. Si
alguien altera un registro y recalcula su huella y todas las posteriores, cada
registro vuelve a cuadrar con sus datos y con el anterior, y la validación pasa
sin incidencias. Esa garantía no la aporta la huella, sino otros mecanismos: la
firma electrónica de los registros en los SIF que no son VERI\*FACTU, y la
remisión inmediata de cada registro a la AEAT en los que sí lo son. Esta
herramienta no comprueba ninguno de los dos.

El primer registro de la lista se trata como el primer registro del sistema.
Si se valida un tramo parcial de una cadena, su primer registro dará E02, porque
su campo `Huella` apunta a un registro que no está en la lista. En ese caso, el
E02 de la posición 0 no indica por sí solo una rotura: puede significar
simplemente que el tramo no empieza en el origen.

## Las ambigüedades

La especificación deja abiertos varios puntos que cambian la huella: por
ejemplo, si `123.1` y `123.10` deben dar la misma, qué caracteres cuentan como
espacio al recortar los valores, o qué hacer si un valor contiene `&` o `=`.
Esta implementación no resuelve ninguno: hace lo mínimo que reproduce los
vectores oficiales. Un sistema que los haya resuelto de otra forma puede
obtener E01 en registros que, según su lectura, son correctos. La
especificación tampoco dice si hay que escapar `&` y `=`, y esta implementación
no lo hace. Eso permitiría que dos registros distintos produjeran la misma
huella, pero solo con valores que el esquema XSD de la AEAT no admite: la
garantía existe, aunque viene de ese esquema y no de la especificación de la
huella. Cada punto, con lo que hace esta
implementación y a quién afecta, está en
[docs/ambiguedades.md](docs/ambiguedades.md).

## Fuentes

- AEAT, "Detalle de las especificaciones técnicas para generación de la huella
  o hash de los registros de facturación", versión 0.1.2, 27/08/2024:
  <https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Veri-Factu_especificaciones_huella_hash_registros.pdf>.
  Lo que se ha extraído de ella para los registros de alta está en
  [docs/campos-huella-alta.md](docs/campos-huella-alta.md), y los dos vectores
  de prueba oficiales forman parte de los tests.
- Calendario de obligatoriedad: tras el
  [Real Decreto-ley 15/2025, de 2 de diciembre](https://www.boe.es/buscar/doc.php?id=BOE-A-2025-24446),
  que modifica el Real Decreto 1007/2023, los sistemas de facturación deben
  estar adaptados antes del 1 de enero de 2027 para los contribuyentes del
  Impuesto sobre Sociedades, y antes del 1 de julio de 2027 para el resto de
  obligados.

## Otros repositorios del proyecto

[calculo-titularidad-real](https://github.com/mshodai/calculo-titularidad-real)
calcula la titularidad real de una sociedad bajo la Ley 10/2010 y bajo el
Reglamento (UE) 2024/1624 (AMLR), y compara los dos regímenes.

[plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc)
calcula el estado de conservación de la documentación de prevención del
blanqueo bajo la Ley 10/2010 y bajo el AMLR.

[plazos-actualizacion-pbc](https://github.com/mshodai/plazos-actualizacion-pbc)
calcula la fecha de la próxima revisión obligatoria de la información de un
cliente bajo la Ley 10/2010 y bajo el AMLR.

[registro-examen-especial-pbc](https://github.com/mshodai/registro-examen-especial-pbc)
comprueba si el registro de un examen especial en el que pudo intervenir un
sistema de IA está completo bajo la Ley 10/2010 y bajo el AMLR.

## Licencia

MIT; el texto completo está en [LICENSE](LICENSE). Cubre el código y la
documentación de este repositorio, no los documentos de la AEAT, que no se
incluyen.

---

Esto es una implementación de referencia probada sobre datos sintéticos. No es
software conforme ni homologado, y no constituye asesoramiento jurídico.
