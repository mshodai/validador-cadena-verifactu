# Ambigüedades de la huella de los registros de alta

Puntos en los que
`docs/fuentes/Veri-Factu_especificaciones_huella_hash_registros.pdf` ("Detalle
de las especificaciones técnicas para generación de la huella o hash de los
registros de facturación", AEAT, versión 0.1.2, 27/08/2024) no determina un
comportamiento único para la huella de los registros de alta. Las referencias
"p. N" remiten a la paginación del PDF, igual que en
[campos-huella-alta.md](campos-huella-alta.md).

Los puntos 1 a 11 proceden del PDF. El punto 12 no: surge al validar una cadena
de registros, algo que el PDF no describe.

**Criterio.** Esta implementación no resuelve ninguna. Donde el documento
admite más de una lectura, el código hace lo mínimo que reproduce los vectores
oficiales (p. 10–11) y lo señala con un comentario `# AMBIGÜEDAD:`. La única
excepción es una parte de la ambigüedad 6, que el esquema XSD resuelve para
`FechaHoraHusoGenRegistro`; está señalada en el código con `# DECISIÓN`. "Esta
implementación" se refiere a `canonicalizar` y `calcular_huella`
(`src/validador_verifactu/huella.py`), a `validar_cadena`
(`src/validador_verifactu/cadena.py`) y a `normalizar_segun_xsd`
(`src/validador_verifactu/xsd.py`).

Los vectores oficiales solo ayudan en un caso: descartan que los valores se
codifiquen como URL (ambigüedad 7). Para el resto no sirven: sus valores no
tienen espacios en los extremos, ni ceros a la derecha, ni caracteres `&`, `=`
o no ASCII.

**A quién afecta.** El emisor calcula la huella al generar el registro; el
validador la recalcula para comprobarla. Si los dos resuelven una ambigüedad de
forma distinta, obtienen huellas distintas para el mismo registro, y el
validador informa E01 aunque el registro sea correcto según la lectura del
emisor. E02 no depende de las ambigüedades 1 a 11: compara las huellas
declaradas, sin recalcular nada. El punto 12 es distinto: afecta solo al
validador y puede dar tanto E01 como E02.

---

## 1. Qué texto se usa en los campos numéricos

**Qué dice la especificación.** "En los campos numéricos se tratarán
indistintamente los valores con una o dos posiciones en los decimales, sin tener
relevancia los ceros a la derecha, considerándose todos igualmente válidos para
la generación de la huella o hash" (p. 6). Ejemplo:
`<ImporteTotal>123.1</ImporteTotal>` "se tratará correctamente, de la misma
forma que si se informara `<ImporteTotal>123.10</ImporteTotal>`" (p. 6). La
tabla de revisiones describe la versión 0.1.2 como "Aclaración tratamiento de
valores numéricos en el hash (ImporteTotal y/o CuotaTotal)" (p. 1).

**Por qué no determina un comportamiento único.** No dice qué texto va en la
concatenación. Caben dos lecturas:

- normalizar a una forma canónica, sin que se diga cuál, de modo que `123.1` y
  `123.10` den la misma huella;
- usar el texto literal del XML y entender que "igualmente válidos" solo
  significa que el XML admite cualquiera de las dos formas.

Las dos lecturas producen huellas distintas para `123.1` y `123.10`.

**Qué hace esta implementación.** Usa el texto literal, tras recortar los
espacios de los extremos. `123.1` y `123.10` dan huellas distintas. La CLI
rechaza los importes escritos como números JSON (`123.10` sin comillas), porque
al leerlos se pierde el texto original (`123.10` se lee como `123.1`); tienen
que llegar como cadenas.

**A quién afecta.** A ambos. Si uno normaliza y el otro no, calculan huellas
distintas para cualquier importe con ceros a la derecha.

## 2. Qué campos son "numéricos"

**Qué dice la especificación.** La p. 6 habla de "los campos numéricos" sin
enumerarlos. Solo la tabla de revisiones (p. 1) menciona "ImporteTotal y/o
CuotaTotal".

**Por qué no determina un comportamiento único.** No queda claro si la regla de
la ambigüedad 1 se limita a esos dos campos o alcanza a otros.

**Qué hace esta implementación.** Ningún campo recibe un tratamiento numérico,
así que la pregunta no se plantea. Habría que responderla si la ambigüedad 1 se
resolviera normalizando.

**A quién afecta.** A ambos, solo si la ambigüedad 1 se resuelve normalizando.

## 3. Valores numéricos fuera del caso de uno o dos decimales

**Qué dice la especificación.** La regla solo habla de valores "con una o dos
posiciones en los decimales" (p. 6).

**Por qué no determina un comportamiento único.** No dice cómo tratar los
valores sin decimales (`123` frente a `123.0` o `123.00`), los ceros a la
izquierda, el signo ni otros separadores decimales.

**Qué hace esta implementación.** Usa el texto literal, como en la
ambigüedad 1.

**A quién afecta.** A ambos.

## 4. El ejemplo Java no aplica la regla numérica

**Qué dice la especificación.** El código de la p. 8 solo aplica `trim()` a cada
valor y sustituye `null` por la cadena vacía. No trata los ceros a la derecha.

**Por qué no determina un comportamiento único.** El texto de la p. 6 y el
único código del documento dicen cosas distintas. Si el código fuera la
referencia, apoyaría la lectura literal de la ambigüedad 1; si lo es el texto,
el código está incompleto. El documento no dice cuál prevalece.

**Qué hace esta implementación.** En los campos numéricos se comporta como el
ejemplo Java (texto literal), pero por el criterio de no resolver, no porque el
código prevalezca. En el recorte de espacios no se comporta igual; véase la
ambigüedad 5.

**A quién afecta.** A ambos, en la medida en que tomen el ejemplo Java como
referencia.

## 5. Qué cuenta como "espacio" al recortar

**Qué dice la especificación.** Se eliminan "los espacios al inicio y al final
de cada valor" (p. 6). Ejemplo: de `<NumSerieFactura> 12345678 / G33
</NumSerieFactura>` "se obtendrá el valor "12345678 / G33"" (p. 6). El ejemplo
Java aplica `valor.trim()` (p. 8).

**Por qué no determina un comportamiento único.** "Espacios" no aclara si
cuentan los tabuladores, los saltos de línea, el espacio de no separación u
otros caracteres en blanco. El ejemplo Java tampoco lo resuelve: el PDF no dice
qué elimina `trim()`. Fuera del PDF, `trim()` de Java y `strip()` de Python, que
parecen equivalentes, eliminan conjuntos de caracteres distintos:

| Caracteres en los extremos                                  | Java `String.trim()` | Python `str.strip()` | ¿Admitidos en XML 1.0? |
|-------------------------------------------------------------|:--------------------:|:--------------------:|:----------------------:|
| Espacio (U+0020)                                            | sí                   | sí                   | sí                     |
| Tabulador, salto de línea y retorno de carro (U+0009, U+000A, U+000D) | sí         | sí                   | sí                     |
| Tabulación vertical, salto de página y separadores de información (U+000B, U+000C, U+001C–U+001F) | sí | sí   | no                     |
| Otros caracteres de control (U+0000–U+0008, U+000E–U+001B)  | sí                   | no                   | no                     |
| Espacio de no separación (U+00A0)                           | no                   | sí                   | sí                     |
| Otros espacios Unicode (U+1680, U+2000–U+200A, U+202F, U+205F, U+3000) | no        | sí                   | sí                     |
| Separadores de línea (U+0085, U+2028, U+2029)               | no                   | sí                   | sí                     |

Fuentes: para Java, la documentación de `String.trim()`, que elimina los
caracteres con código menor o igual que U+0020 (no se ha podido comprobar
ejecutándolo). Para Python, `str.strip()` sin argumentos elimina los caracteres
para los que `str.isspace()` es verdadero; el conjunto se ha obtenido
recorriendo todo Unicode con Python 3.14. Java 11 añadió además
`String.strip()`, con un tercer criterio distinto de los dos anteriores; el
ejemplo del PDF usa `trim()`.

Un caso práctico: si el XML está indentado y el valor queda en su propia línea
(`<NumSerieFactura>` seguido de un salto de línea y sangría), `trim()` y
`strip()` eliminan el salto y la sangría; recortar solo U+0020 no los elimina.

En un registro, que es un documento XML, la tabla se reduce. XML 1.0 no admite
los caracteres de control de la tercera y la cuarta fila, ni siquiera escritos
como referencia de carácter, así que lo que Java recorta y Python no nunca
aparece en un registro. La divergencia entre las dos queda en un solo sentido:
los espacios Unicode de las tres últimas filas, que Python recorta y Java no.
Además, `NumSerieFactura` solo admite ASCII del 32 al 126 (Validaciones,
versión 1.2.2, sección 3.1.3.1, p. 8), y en ese rango el único carácter que se
recorta es el espacio, que las tres variantes tratan igual. La divergencia solo
es alcanzable en los campos cuyo tipo XSD admite cualquier texto
(`IDEmisorFactura` y `Huella`) y en `NumSerieFactura` cuando esa validación no
se aplica con rechazo (ver la ambigüedad 7).

**Qué hace esta implementación.** Solo elimina el espacio U+0020
(`valor.strip(" ")`), que es la lectura más literal de "espacios" y reproduce el
ejemplo de la p. 6 y los vectores oficiales. No equivale a `strip()` de Python
ni a `trim()` de Java. La excepción es `FechaHoraHusoGenRegistro`: antes de este
recorte pasa por el colapsado de su tipo XSD (ambigüedad 6), que en ese campo
elimina también tabuladores, saltos de línea y retornos de carro.

**A quién afecta.** A ambos. Un emisor que siga el ejemplo Java y tenga un
tabulador o un salto de línea en el extremo de un valor que no sea la fecha de
generación obtendrá una huella que esta implementación considera E01. Con un
espacio de no separación ocurre lo mismo frente a un emisor que use `strip()`
de Python.

## 6. Qué es "la misma información contenida en el campo del fichero XML"

**Qué dice la especificación.** "Los valores de los campos deberán tener la
misma información contenida en el campo correspondiente del fichero XML"
(p. 6). La cadena se codifica en UTF-8 (p. 7).

**Por qué no determina un comportamiento único.** No aclara si el valor es el
texto tal como aparece en el fichero, con referencias de entidad o de carácter
como `&amp;` sin resolver, o el valor ya interpretado por un procesador XML.
Tampoco dice nada sobre normalización Unicode antes de codificar en UTF-8: por
ejemplo, "é" como un solo carácter o como "e" seguida de un acento combinable,
que dan bytes distintos.

En los campos tipados, el texto y el valor pueden no coincidir. En el esquema
XSD (`SuministroInformacion.xsd`), siete de los ocho campos que entran en la
huella derivan de `xs:string`, cuya faceta `whiteSpace` es `preserve`: su texto
es su valor. El octavo, `FechaHoraHusoGenRegistro`, es `xs:dateTime`, cuya
faceta es `collapse` y no se puede cambiar (XML Schema 1.0, parte 2, §3.2.7 y
§4.3.6). En un XML indentado, el texto literal de ese elemento lleva saltos de
línea y sangría, y su valor según el esquema no. Un analizador XML corriente
devuelve el texto; uno que aplique el esquema devuelve el valor.

**Qué hace esta implementación.** En `FechaHoraHusoGenRegistro` resuelve la
ambigüedad a favor del valor según el esquema. Antes de calcular la huella,
`normalizar_segun_xsd` aplica el colapsado de `xs:dateTime`: sustituye cada
secuencia de espacio, tabulador, salto de línea o retorno de carro (U+0020,
U+0009, U+000A, U+000D) por un espacio y elimina los de los extremos. No toca
el espacio de no separación ni otros espacios Unicode, que XML Schema no
considera espacio en blanco. Hay tres razones para resolverla aquí:

- el esquema fija la faceta de forma normativa, así que "la misma información
  contenida en el campo" es el valor colapsado;
- con ese valor coinciden el `trim()` de Java, el `strip()` de Python y el
  propio esquema; solo la lectura anterior de esta implementación daba otro;
- el colapsado es idempotente, así que el resultado es el mismo si la entrada
  ya venía normalizada o si trae el texto literal del XML, y el validador no
  necesita saber cuál de los dos recibe.

Sin esto, un registro conforme con el XML indentado daba E01. No todos los
validadores XSD aplican la norma igual: libxml2 2.14 rechaza un `xs:dateTime`
con espacio en blanco alrededor, aunque la norma lo admite.

En el resto de campos, y en todo lo demás de este punto, usa el valor
exactamente como lo recibe: no resuelve referencias ni aplica normalización
Unicode. La decisión recae en quien extrae los valores del XML para construir la
entrada (por ejemplo, el JSON de la CLI); si lo hace con un procesador XML, las
referencias llegarán resueltas.

**A quién afecta.** A ambos.

## 7. Valores que contienen `&` o `=`

**Qué dice la especificación.** La cadena tiene la forma
`nombreCampo1=valorCampo1&nombreCampo2=valorCampo2&nombreCampoN=valorCampoN`
(p. 6). El código de la p. 8 define un método `getValorCampoEncoded`, que aplica
`URLEncoder.encode(valor, "UTF-8")`, pero no lo llama nunca: la cadena de alta se
construye con `getValorCampo`, sin codificar.

**Por qué no determina un comportamiento único.** El documento no dice qué hacer
si un valor contiene `&` o `=`, ni si la codificación URL forma parte de la
especificación. Los vectores oficiales sí descartan codificar el valor entero
con `URLEncoder`: contienen `/`, `:` y `+` (`12345678/G33`,
`2024-01-01T19:20:30+01:00`), que se convertirían en `%2F`, `%3A` y `%2B`, y las
huellas oficiales solo se reproducen sin codificar. Lo que queda abierto es si
`&` y `=` deben escaparse de alguna otra forma: los vectores no contienen
ninguno de los dos y el documento no lo dice.

**¿Pueden dos registros distintos producir la misma cadena?** La serialización
no es inyectiva por diseño: como no se escapa nada, un valor que contenga
`&Nombre=` puede imitar el límite entre dos campos. Si cada campo admitiera
cualquier texto, dos registros distintos podrían dar la misma cadena y, por
tanto, la misma huella. Por ejemplo, `NumSerieFactura` =
`1&FechaExpedicionFactura=01-01-2024` con `FechaExpedicionFactura` vacía, y
`NumSerieFactura` = `1` con `FechaExpedicionFactura` =
`01-01-2024&FechaExpedicionFactura=`, dan los dos
`…&NumSerieFactura=1&FechaExpedicionFactura=01-01-2024&FechaExpedicionFactura=&TipoFactura=…`.
**Este ejemplo solo funciona con valores que la AEAT rechaza**: los dos
registros llevan una `FechaExpedicionFactura` que no cumple el esquema XSD, y el
primero, además, un `=` en `NumSerieFactura`, que el documento de Validaciones
prohíbe.

Con registros válidos la colisión no es posible, pero la garantía no está en la
especificación de la huella, que no la menciona. Está en otros dos documentos:

- **El esquema XSD** (`SuministroInformacion.xsd`). No restringe los caracteres
  de `NumSerieFactura`: su tipo, `TextoIDFacturaType`, es un `string` de 1 a 60
  caracteres sin `pattern`. Tampoco los de `IDEmisorFactura` (`NIFType`,
  `string` de longitud 9) ni los de `Huella` (`TextMax64Type`, `string` de
  hasta 64). Pero cierra el formato de los otros cinco campos (fecha con
  patrón, enumeración, importes con patrón y `xs:dateTime`, ninguno de los
  cuales admite `&` ni `=`) y limita la longitud de esos tres. Eso basta,
  porque imitar un límite exige meter dentro de un campo libre un separador
  completo y todo lo que hay hasta el siguiente campo libre. `&NumSerieFactura=`
  mide 17 caracteres y no cabe en los 9 de `IDEmisorFactura`. Entre
  `NumSerieFactura` y `Huella` hay cuatro campos cerrados, y el tramo más corto
  que habría que desplazar
  (`&FechaExpedicionFactura=dd-mm-aaaa&TipoFactura=F1&CuotaTotal=1&ImporteTotal=1&Huella=`)
  mide 85 caracteres, más que los 60 y los 64 permitidos. Sin esos límites de
  longitud, la colisión sí se puede construir respetando los formatos cerrados.
- **El documento de Validaciones** (AEAT, versión 1.2.2, sección 3.1.3.1, p. 8).
  `NumSerieFactura` "solo puede contener caracteres ASCII del 32 a 126" y no
  admite `"` (34), `'` (39), `<` (60), `>` (62) ni `=` (61). Si ningún valor
  contiene `=`, todos los `=` de la cadena son separadores y la cadena se
  descompone de una sola forma, aunque haya `&`. El `&` (ASCII 38) no figura
  entre los caracteres prohibidos; con `&` y sin `=` tampoco hay colisión.

Las dos conclusiones se comprueban en
[`tests/test_colision.py`](https://github.com/mshodai/validador-cadena-verifactu/blob/main/tests/test_colision.py), que cuenta todas las
formas de descomponer una cadena en valores válidos. Con valores que solo
contienen `&`, y con 20 000 registros aleatorios con `&` y `=` en los tres
campos libres dentro de las longitudes del XSD, siempre hay una única
descomposición. Sin esos límites de longitud, el mismo test construye una
colisión.

Esas garantías tienen límites:

- Son comprobaciones que la AEAT hace al recibir los registros. En la modalidad
  NO VERI\*FACTU los registros se conservan en local y pueden no enviarse nunca;
  mientras no se envían, nada comprueba que cumplan el XSD ni las validaciones.
- Cuando se envían por requerimiento, las validaciones de negocio no rechazan
  registros: "todos los errores provocados por validaciones de negocio se
  marcarán como errores admisibles", salvo los de identificación de NIF o
  IdOtro (Validaciones, sección 4.3.2, p. 22). Un `NumSerieFactura` con `=` se
  aceptaría con un aviso. El formato de `Huella` (64 caracteres hexadecimales
  en mayúsculas) tampoco provoca nunca un rechazo, solo un aviso (sección
  3.1.3.18, p. 15). En cambio, un envío que no cumple el esquema XSD se rechaza
  entero (sección 4.1, p. 20). Para los registros que llegan a enviarse, la
  garantía efectiva es la del XSD.

Aparte de esto, la cadena no distingue lo que la especificación manda ignorar:
los espacios de los extremos (ambigüedad 5) y un campo ausente frente a uno
vacío. Eso es deliberado, no una colisión.

**Qué hace esta implementación.** No codifica: usa el valor tal cual, que es lo
que reproduce los vectores. Tampoco comprueba el XSD ni las validaciones, así
que dos entradas JSON con valores fuera de esos formatos pueden producir la
misma cadena.

**A quién afecta.** A ambos si uno de los dos escapa `&` o `=` y el otro no.
La colisión solo afecta a registros que no cumplen el XSD: registros NO
VERI\*FACTU que nunca se envían, o entradas del validador que no proceden de un
XML válido.

## 8. Formato de `FechaExpedicionFactura` en el ejemplo Java

**Qué dice la especificación.** Según la p. 6, el valor es el contenido del XML.
Sin embargo, `calcularHuellaAlta` (p. 8) recibe la fecha de expedición como
`Date` y la pasa por un método `formatea(fechaExpedicion)` que no aparece
definido en el documento. El único dato de formato es el ejemplo `01-01-2024`
(p. 10–11).

**Por qué no determina un comportamiento único.** No queda claro si la fecha se
transforma o se toma literal del XML, ni con qué patrón se formatearía.

**Qué hace esta implementación.** Toma la fecha literal, sin reformatearla. Los
corpus sintéticos de `fixtures/` usan el formato `dd-mm-aaaa` de los vectores.

**A quién afecta.** A ambos.

## 9. El ejemplo Java no se puede ejecutar tal como está

**Qué dice la especificación.** Además de `formatea`, el código de la p. 8 usa
una clase `Base16` con constructor `Base16(false)` y método `encodeAsString`, que
el documento no define ni importa, y no explica el significado del argumento
`false`. Hay además incoherencias menores:

- el parámetro se llama `fechaHoraUsoRegistro` ("Uso"), pero el campo es
  `FechaHoraHusoGenRegistro` ("Huso");
- los ejemplos de las p. 10–11 llaman a una función `calcularHuella(...)` con la
  cadena ya montada, y esa función no existe en el código de la p. 8 (allí están
  `getHashVerifactu(String)` y `calcularHuellaAlta(...)`, con parámetros
  separados).

**Por qué no determina un comportamiento único.** El código no puede servir como
implementación de referencia ejecutable. En particular, el formato de salida
(hexadecimal en mayúsculas) sale solo del texto de la p. 9, porque no se sabe qué
hace `Base16(false)`.

**Qué hace esta implementación.** No toma el ejemplo Java como referencia. Sigue
el texto de la p. 9: hexadecimal en mayúsculas (`hexdigest().upper()`). El
resultado se comprueba contra los vectores oficiales.

**A quién afecta.** A ambos, como referencia: quien porte el ejemplo Java tiene
que completar los huecos con su propio criterio.

## 10. Qué algoritmo se usa y dónde se declara

**Qué dice la especificación.** "El algoritmo a utilizar se detalla en la Lista
L12 del apartado 6 del anexo de la orden" y "en la fecha de publicación de este
documento el único algoritmo permitido es SHA-256" (p. 4). La orden aparece
como "Orden XXXXXXX" (p. 3), un marcador sin resolver.

**Por qué no determina un comportamiento único.** El PDF no permite saber si la
lista L12 admite o admitirá otros algoritmos. En ese caso, la longitud de 64
caracteres de la p. 9 podría no aplicarse, y el documento tampoco dice cómo se
indica en el registro qué algoritmo se ha usado.

El esquema XSD responde a la mayor parte. `RegistroAlta` tiene un elemento
obligatorio `TipoHuella`, de tipo `TipoHuellaType`, que es una enumeración con
un único valor, `01`, documentado como "SHA-256" (`SuministroInformacion.xsd`;
el registro de anulación tiene el mismo elemento). El registro declara así el
algoritmo, y el esquema vigente no admite otro: un registro que declare otro
valor no cumple el esquema y se rechaza entero al enviarse (Validaciones,
versión 1.2.2, sección 4.1, p. 20). El documento de Validaciones no menciona
`TipoHuella`, pero sí exige que la huella del registro anterior tenga el formato
de salida de SHA-256, "64 caracteres en hexadecimal y en mayúsculas" (sección
3.1.3.18, p. 15).

Queda abierto lo siguiente:

- el XSD no cita la lista L12, así que no puede confirmarse con estos documentos
  que `TipoHuellaType` la reproduzca;
- si una versión futura del esquema añadiera otro algoritmo, `TipoHuella`
  indicaría cuál se usó, pero la longitud de la p. 9 y la validación de formato
  de Validaciones tendrían que cambiar con él.

**Qué hace esta implementación.** Usa siempre SHA-256, que es el único valor
que admite `TipoHuella` en el esquema vigente. No lee `TipoHuella`: no es uno
de los ocho campos de la huella y la entrada no lo incluye. Un registro cuya
huella se hubiera calculado con otro algoritmo daría E01.

**A quién afecta.** A ambos, solo si el esquema llega a admitir otro algoritmo.

## 11. Doble criterio de orden, uno de ellos no verificable

**Qué dice la especificación.** Los campos se toman "en el orden enunciado, que
coincide con su aparición en los correspondientes diseños de registros
publicados en el anexo de la orden" (p. 5).

**Por qué no determina un comportamiento único.** El anexo no está incluido en
el PDF, así que la coincidencia no se puede comprobar con este documento, y el
documento no dice qué criterio prevalece si no coincidieran.

**Qué hace esta implementación.** Usa el orden enunciado en la p. 5. Los
vectores oficiales se reproducen con ese orden.

**A quién afecta.** A ambos.

---

## 12. Cómo se comparan las huellas al validar

Esta ambigüedad **no procede del PDF, sino del acto de validar**. El documento
define cómo se calcula la huella, pero no cómo se comprueba. Surge en
`validar_cadena`, no en `canonicalizar`.

**Qué dice la especificación.** Nada sobre comparar huellas. Define cómo se
calcula la huella (p. 5–7) y su formato: "en sistema hexadecimal", "en
mayúsculas" y de 64 caracteres (p. 9). También dice dónde se escribe la huella
del propio registro (`RegistroAlta/Huella`, p. 9) y dónde la del anterior
(`Encadenamiento/RegistroAnterior/Huella`, p. 5), y que en el primer registro
"no será necesario informar los campos de los bloques "RegistroAnterior""
(p. 9). El recorte de los espacios de los extremos se define para los valores
que entran en la concatenación (p. 6), no para ninguna otra operación.

**Por qué no determina un comportamiento único.** Validar exige dos
comparaciones que el documento no describe: la huella declarada frente a la
recalculada (E01), y el campo `Huella` frente a la huella declarada del
registro anterior (E02). El documento no dice si esas comparaciones deben
tolerar diferencias de forma:

- **Espacios en los extremos.** El campo `Huella` entra recortado en la
  concatenación, así que `" 3C46…"` y `"3C46…"` producen la misma huella del
  registro. No se dice si, al comprobar el encadenamiento, esos dos valores
  cuentan como iguales.
- **Mayúsculas y minúsculas.** La p. 9 exige mayúsculas, pero no dice si una
  huella en minúsculas es otra huella o la misma huella mal formateada.
- **Qué es un campo `Huella` "vacío" en el primer registro.** Puede estar
  ausente, sin contenido o solo con espacios.

**Qué hace esta implementación.** Compara el texto exacto, sin recortar ni
cambiar mayúsculas y minúsculas. Un campo ausente o con valor `None` se trata
como vacío, igual que en `canonicalizar`. En consecuencia:

- una `HuellaPropia` en minúsculas o con espacios en los extremos da E01,
  aunque sea la huella correcta. Si el registro siguiente escribe esa huella en
  mayúsculas, como exige la p. 9, ese registro da además E02;
- un campo `Huella` con espacios en los extremos da E02, aunque la huella del
  propio registro, que lo recorta, sea correcta;
- en el primer registro, `Huella` = `"   "` da E02, aunque `canonicalizar` lo
  trate como vacío al calcular la huella.

**A quién afecta.** Al validador. El emisor no compara huellas; solo influye en
el resultado si escribe las huellas en minúsculas o con espacios en los
extremos.
