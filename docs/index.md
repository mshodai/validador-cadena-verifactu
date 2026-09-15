---
title: "¿Pueden dos facturas distintas tener la misma huella en VERI*FACTU?"
description: "La huella de los registros de facturación concatena los campos como nombre=valor&nombre=valor sin escapar los separadores. Por qué, aun así, dos registros válidos no pueden producir la misma cadena, y de qué documento depende."
---

# ¿Pueden dos facturas distintas tener la misma huella en VERI\*FACTU?

Cada registro de facturación de alta lleva una huella: un SHA-256 calculado
sobre ocho de sus campos, uno de los cuales es la huella del registro anterior.
Si dos
registros distintos pudieran producir la misma huella, la huella dejaría de
identificar un registro concreto. Este artículo sigue esa pregunta a través de
los documentos de la AEAT y llega a una respuesta que no está donde cabría
esperarla.

"Distintas" significa aquí distintas en alguno de los ocho campos que entran en
la huella. Lo que no entra en ella (el desglose, los destinatarios) no la
cambia, por diseño.

## La pregunta

La especificación de la huella (AEAT, "Detalle de las especificaciones técnicas
para generación de la huella o hash de los registros de facturación", versión
0.1.2, 27/08/2024) manda concatenar los ocho campos en un orden fijo (p. 5), con
la forma
`nombreCampo1=valorCampo1&nombreCampo2=valorCampo2&nombreCampoN=valorCampoN`
(p. 6), y calcular el SHA-256 (p. 4) de esa cadena codificada en UTF-8 (p. 7).
Para un registro de alta, la cadena queda así:

```
IDEmisorFactura=…&NumSerieFactura=…&FechaExpedicionFactura=…&TipoFactura=…&CuotaTotal=…&ImporteTotal=…&Huella=…&FechaHoraHusoGenRegistro=…
```

El documento no dice qué hacer si un valor contiene `&` o `=`. Su código de
ejemplo en Java define un método que codifica los valores como URL, pero no lo
llama nunca: la cadena se construye con los valores sin codificar (p. 8). Los
vectores de prueba oficiales confirman que no se codifican, porque contienen
`/`, `:` y `+` y solo se reproducen con esos caracteres tal cual (p. 10 y 11).

Si los separadores no se escapan, ¿puede un valor imitar el límite entre dos
campos?

## La respuesta que parece obvia

`NumSerieFactura` es el número de serie de la factura, un texto que elige el
emisor. Si admite cualquier carácter, un número de serie puede contener un
separador falso. Estos dos registros difieren en `NumSerieFactura` y en
`FechaExpedicionFactura`:

| Campo                    | Registro A                            | Registro B                             |
|--------------------------|---------------------------------------|----------------------------------------|
| `NumSerieFactura`        | `1&FechaExpedicionFactura=01-01-2024` | `1`                                    |
| `FechaExpedicionFactura` | *(vacío)*                             | `01-01-2024&FechaExpedicionFactura=`   |

Con el resto de campos iguales, los dos producen la misma cadena:

```
IDEmisorFactura=00000000T&NumSerieFactura=1&FechaExpedicionFactura=01-01-2024&FechaExpedicionFactura=&TipoFactura=F1&CuotaTotal=12.35&ImporteTotal=123.45&Huella=3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60&FechaHoraHusoGenRegistro=2024-01-01T19:20:30+01:00
```

y, por tanto, la misma huella,
`2C41A8D6971853A6274525A2DAE6EE57C9BAC8C1A9BC8457167188EF1AE72EA3`. La
serialización, tal como la describe la especificación, no es inyectiva.

El ejemplo tiene un detalle que conviene retener: además de un número de serie
con separadores, necesita una `FechaExpedicionFactura` que no es una fecha.

## Por qué esa respuesta es incorrecta

El número de serie no admite cualquier carácter. El documento de Validaciones
de la AEAT establece que `NumSerieFactura` "solo puede contener caracteres ASCII
del 32 a 126 (caracteres imprimibles)" y excluye expresamente `"` (34), `'`
(39), `<` (60), `>` (62) y `=` (61) (AEAT, "Sistemas Informáticos de
Facturación y Sistemas VERI\*FACTU. Validaciones", versión 1.2.2, 08/04/2026,
sección 3.1.3.1, p. 8). El registro A queda descartado.

El `&` (ASCII 38) no figura entre los caracteres prohibidos, pero sin `=` no
basta. Si ningún valor contiene `=`, todos los `=` de la cadena son los que
siguen a un nombre de campo, y la cadena se descompone de una sola manera
aunque haya `&` dentro de los valores.

## Por qué esa tampoco es la razón de fondo

La prohibición del `=` resuelve el caso, pero no es lo que impide la colisión.
Hay dos motivos.

El primero es su alcance. Es una validación de negocio que la AEAT aplica al
recibir los registros, y en la remisión bajo requerimiento de un sistema NO
VERI\*FACTU "todos los errores provocados por validaciones de negocio se
marcarán como errores admisibles", salvo los de identificación de NIF o IdOtro
(Validaciones, versión 1.2.2, sección 4.3.2, p. 22). Un número de serie con `=`
se aceptaría con un aviso, no se rechazaría. Y un sistema NO VERI\*FACTU
conserva sus registros en local, sin enviarlos salvo requerimiento (AEAT,
"Aclaraciones a dudas de los desarrolladores", versión 1.3, 04/12/2025, sección
18, p. 38).

El segundo es que la colisión es imposible incluso permitiendo `=`. El esquema
XSD de suministro (AEAT, `SuministroInformacion.xsd`, sin versión declarada;
fecha de publicación según el servidor, 11/01/2026) no restringe los
caracteres de tres de los ocho campos: `IDEmisorFactura` (`NIFType`, texto de
longitud 9), `NumSerieFactura` (`TextoIDFacturaType`, texto de 1 a 60, sin
patrón) y `Huella` (`TextMax64Type`, texto de hasta 64). Pero los otros cinco
tienen formato cerrado: la fecha de expedición sigue el patrón `dd-mm-aaaa`, el
tipo de factura es una enumeración, los importes tienen un patrón numérico y la
fecha de generación es un `xs:dateTime`. Ninguno admite `&` ni `=`. Un registro
con un valor que no cumple el esquema se rechaza. Se rechaza solo ese registro,
porque el mensaje entero solo se rechaza por errores estructurales o por
errores sintácticos en la cabecera (Validaciones, versión 1.2.2, sección 3.1,
p. 6). A diferencia de las validaciones de negocio, esto también se aplica
en la remisión bajo requerimiento, en la que el servicio de la AEAT solo
rechaza registros que incumplan el esquema XML o cuyo NIF de destinatario no
exista en el censo (Aclaraciones a dudas de los desarrolladores, versión 1.3,
sección 18, p. 38).

Con esas restricciones, imitar un límite exige meter dentro de un campo libre
un separador completo y todo lo que hay hasta el siguiente campo libre:

- `&NumSerieFactura=` mide 17 caracteres y no cabe en los 9 de
  `IDEmisorFactura`.
- Entre `NumSerieFactura` y `Huella` hay cuatro campos cerrados. El tramo más
  corto que habría que desplazar,
  `&FechaExpedicionFactura=dd-mm-aaaa&TipoFactura=F1&CuotaTotal=1&ImporteTotal=1&Huella=`,
  mide 85 caracteres. Los campos libres admiten 60 y 64.

Por eso el ejemplo anterior necesitaba una fecha que no es una fecha: con los
formatos cerrados del esquema, desplazar un límite exige un campo libre más
largo de lo que el esquema permite.

El test
[`tests/test_colision.py`](https://github.com/mshodai/validador-cadena-verifactu/blob/main/tests/test_colision.py)
lo comprueba contando todas las formas de descomponer una cadena en valores
que cumplen el esquema. Con 20 000 registros aleatorios que llevan `&` y `=` en
los tres campos libres, casi todos con separadores falsos dentro de los
valores, siempre hay una única descomposición. El mismo test construye una
colisión en cuanto se quitan los límites de longitud, respetando todos los
formatos cerrados.

## La conclusión

La serialización de la huella no es inyectiva por diseño. Para registros que
cumplen el esquema lo es, pero por los límites de longitud del XSD y por los
formatos cerrados de los campos que quedan entre los libres. Nada en los
documentos indica que esos límites se fijaran con ese fin, y la especificación
de la huella no los menciona. La prohibición del `=` en el número de serie es
una segunda barrera, más fácil de razonar, que no se aplica con rechazo en el
caso en el que más importaría.

Dejando aparte lo que la especificación manda ignorar (los espacios de los
extremos de cada valor y la diferencia entre un campo ausente y uno vacío), dos
registros válidos distintos no producen la misma cadena de entrada. Solo
podrían compartir huella mediante una colisión del propio SHA-256, que es otra
cuestión.

Para quien tiene que verificar una cadena, esto tiene tres consecuencias:

- **La garantía depende de que los registros cumplan el esquema.** Un
  verificador que recibe los valores ya extraídos, sin comprobar el XSD, no
  puede dar por hecho que huellas iguales implican registros iguales. En la
  modalidad NO VERI\*FACTU los registros pueden no haberse enviado nunca, así
  que nadie ha comprobado que cumplan el esquema.
- **La garantía puede cambiar sin que cambie la especificación de la huella.**
  Si una versión futura del esquema ampliara lo suficiente esas longitudes, o
  abriera el formato de alguno de los campos intermedios, la colisión volvería
  a ser construible y la especificación de la huella seguiría diciendo lo
  mismo.
- **La razón está en un documento distinto del que se lee para implementar la
  huella.** Quien implemente la huella a partir de su especificación no
  encontrará ahí ninguna advertencia sobre `&` y `=`. Encontrará la
  explicación, si la busca, en el esquema.

El detalle de este punto y de las demás ambigüedades de la especificación está
en [ambiguedades.md](ambiguedades.md), en el punto 7. El código, los tests y las
fuentes están en el
[repositorio](https://github.com/mshodai/validador-cadena-verifactu).

Este es uno de tres casos en los que la decisión sobre cómo se construye la
cadena la toma el esquema y no la especificación de la huella. Los otros dos,
el algoritmo y el espacio en blanco, están en
[¿Basta la especificación de la huella de VERI\*FACTU para implementarla?](el-esquema-decide.md).
Qué valida la AEAT cuando recibe los registros por un requerimiento, y qué no
figura entre sus validaciones, está en
[¿Qué comprueba Hacienda al recibir tus registros de facturación en un requerimiento?](que-comprueba-hacienda.md).

---

Este análisis es de arquitectura de software, no asesoramiento jurídico.
