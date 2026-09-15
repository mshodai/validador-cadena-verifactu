---
title: "¿Basta la especificación de la huella de VERI*FACTU para implementarla?"
description: "Tres decisiones sobre la huella de los registros de facturación que la especificación de la huella no toma y que fija el esquema XSD: el algoritmo, el espacio en blanco y la inyectividad de la cadena."
---

# ¿Basta la especificación de la huella de VERI\*FACTU para implementarla?

Para implementar la huella de los registros de facturación se lee su
especificación: AEAT, "Detalle de las especificaciones técnicas para generación
de la huella o hash de los registros de facturación", versión 0.1.2,
27/08/2024. Son trece páginas que definen qué campos entran, en qué orden, con
qué formato se concatenan, con qué algoritmo se calcula la huella y cómo se
escribe el resultado.

El propio documento remite fuera de sí. El orden de los campos "coincide con su
aparición en los correspondientes diseños de registros publicados en el anexo
de la orden" (p. 5), y el nombre de cada campo "será un valor constante tal y
como se describe en el XML del diseño de registro" (p. 6). Esa remisión no se
limita a los nombres. Hay decisiones sobre cómo se construye la cadena que la
especificación no menciona y que fija el esquema XSD de suministro (AEAT,
`SuministroInformacion.xsd`). Este artículo recorre tres.

## 1. El algoritmo

La especificación dice: "El algoritmo a utilizar se detalla en la Lista L12 del
apartado 6 del anexo de la orden. En la fecha de publicación de este documento
el único algoritmo permitido es SHA-256" (p. 4). La orden a la que remite
aparece en el mismo documento como "Orden XXXXXXX" (p. 3), un marcador que
nunca se rellenó. El documento no dice si esa lista admite o admitirá otros
algoritmos, ni cómo indica un registro cuál ha usado.

El esquema responde a las dos preguntas para la versión vigente. El tipo del
registro de alta (`RegistroFacturacionAltaType`) tiene un elemento
`TipoHuella`, de tipo `TipoHuellaType`, sin `minOccurs`, así que es obligatorio.
`TipoHuellaType` es una enumeración con un único valor, `01`, documentado como
"SHA-256". El registro de anulación tiene el mismo elemento. Un registro que
declare otro valor no cumple el esquema y se rechaza al enviarse. Se rechaza
solo ese registro, porque el mensaje entero solo se rechaza por errores
estructurales o por errores sintácticos en la cabecera (AEAT, "Sistemas
Informáticos de Facturación y Sistemas VERI\*FACTU. Validaciones", versión
1.2.2, 08/04/2026, sección 3.1, p. 6). El
documento de Validaciones completa el cuadro por el lado del formato: la huella
del registro anterior debe tener "64 caracteres en hexadecimal y en
mayúsculas" (sección 3.1.3.18, p. 15).

La especificación de la huella no menciona `TipoHuella`. El esquema tampoco
cita la lista L12, así que estos documentos no permiten confirmar que
`TipoHuellaType` sea esa lista. Pero, para quien construye o comprueba una
cadena hoy, la cuestión que la especificación deja abierta la cierra el
esquema: hay un campo obligatorio que declara el algoritmo y admite un solo
valor.

## 2. El espacio en blanco

La especificación manda que los valores tengan "la misma información contenida
en el campo correspondiente del fichero XML, pero eliminando los espacios al
inicio y al final de cada valor" (p. 6). No dice qué caracteres cuentan como
espacio. Tampoco dice que, según el tipo del campo en el esquema, el valor del
elemento puede no coincidir con su texto.

En XML Schema, cada tipo tiene una faceta `whiteSpace` que fija qué se hace con
el espacio en blanco antes de validar. El esquema de suministro no la
redefine en ningún tipo, así que cada campo hereda la de su tipo base (XML
Schema 1.0, parte 2, §4.3.6):

| Campo                      | Tipo en el XSD         | Tipo base     | `whiteSpace` |
|----------------------------|------------------------|---------------|--------------|
| `IDEmisorFactura`          | `NIFType`              | `xs:string`   | `preserve`   |
| `NumSerieFactura`          | `TextoIDFacturaType`   | `xs:string`   | `preserve`   |
| `FechaExpedicionFactura`   | `fecha`                | `xs:string`   | `preserve`   |
| `TipoFactura`              | `ClaveTipoFacturaType` | `xs:string`   | `preserve`   |
| `CuotaTotal`               | `ImporteSgn12.2Type`   | `xs:string`   | `preserve`   |
| `ImporteTotal`             | `ImporteSgn12.2Type`   | `xs:string`   | `preserve`   |
| `Huella`                   | `TextMax64Type`        | `xs:string`   | `preserve`   |
| `FechaHoraHusoGenRegistro` | `xs:dateTime`          | —             | `collapse`   |

En los siete campos `preserve`, el texto del elemento es su valor. El espacio
en blanco que haya en los extremos forma parte de él, y lo único que lo quita es
el recorte que manda la especificación. En cuatro de esos siete ni siquiera
puede haberlo, porque un patrón o una enumeración lo impiden. Que los importes
sean texto con patrón y no `xs:decimal`, que colapsaría el espacio en blanco,
es también una decisión del esquema.

El octavo es distinto. `xs:dateTime` tiene la faceta `collapse` fijada por la
norma (XML Schema 1.0, parte 2, §3.2.7): antes de validar se eliminan el
espacio, el tabulador, el salto de línea y el retorno de carro de los extremos.
Si el XML está indentado y la fecha de generación queda en su propia línea, el
texto del elemento lleva un salto de línea y sangría, y su valor según el
esquema no. Un analizador XML corriente devuelve el texto; uno que aplique el
esquema devuelve el valor. La especificación, al hablar solo de "espacios", no
avisa de que en este campo la respuesta la da el tipo.

Este mismo proyecto tenía ahí un fallo. Recortaba solo el carácter espacio,
que es la lectura más literal de la especificación, y con un XML indentado
dejaba el salto de línea dentro de la fecha. La huella recalculada no coincidía
con la declarada, y el validador marcaba E01 en un registro conforme. El commit
[`9264557`](https://github.com/mshodai/validador-cadena-verifactu/commit/9264557215a3ff23c35a93e7fbdcea7268d990f1)
lo corrige: antes de calcular la huella aplica a ese campo el colapsado de
`xs:dateTime`. El colapsado es idempotente, así que da el mismo resultado si la
entrada trae el texto literal o el valor ya normalizado. La decisión y sus
motivos están en el punto 6 de [ambiguedades.md](ambiguedades.md).

Los validadores tampoco coinciden en esto. libxml2 2.14 rechaza un
`xs:dateTime` con espacio en blanco alrededor, aunque la norma lo admite. Eso
no cambia qué valor define el esquema, pero sí significa que un mismo registro
indentado puede pasar o no una validación según la herramienta.

## 3. La inyectividad

La especificación concatena los campos como `nombre=valor&nombre=valor` sin
escapar los separadores (p. 6), así que un valor podría imitar el límite entre
dos campos. El [primer artículo](index.md) sigue esa pregunta hasta el final.
En resumen:

- El documento de Validaciones prohíbe el `=` en `NumSerieFactura` (versión
  1.2.2, sección 3.1.3.1, p. 8), pero esa validación no provoca rechazo en la
  remisión bajo requerimiento de un sistema NO VERI\*FACTU (sección 4.3.2,
  p. 22).
- Lo que impide la colisión son las longitudes máximas del esquema (`NIFType`,
  9 caracteres; `TextoIDFacturaType`, 60; `TextMax64Type`, 64), junto con los
  formatos cerrados de los campos intermedios. El tramo más corto que habría
  que desplazar mide 85 caracteres.

El test
[`tests/test_colision.py`](https://github.com/mshodai/validador-cadena-verifactu/blob/main/tests/test_colision.py)
lo comprueba, y construye una colisión en cuanto se quitan esos límites. Ningún
documento indica que las longitudes se fijaran con ese fin, y la
especificación de la huella no las menciona.

## Lo que significa para quien implementa

La especificación de la huella no es autosuficiente, y lo dice ella misma al
remitir al diseño de registro para los nombres y el orden, y a una orden sin
identificar para el algoritmo. Las tres decisiones de este artículo tienen la
misma forma: la especificación deja una pregunta abierta o ni la plantea, y la
respuesta está en el esquema.

- **El algoritmo** se declara en `TipoHuella`, que la especificación no nombra.
- **El valor de la fecha de generación** es el que resulta de su tipo, no el
  texto del elemento.
- **La garantía de que dos registros válidos no comparten cadena** viene de
  unas longitudes máximas que la especificación no cita.

Por eso el esquema no es solo validación de formato. Es una fuente normativa,
en el sentido técnico, de cómo se construye la cadena: una implementación que
lo ignore puede calcular mal la huella, como le pasó a este proyecto, o
apoyarse en una garantía sin saber de dónde viene. De ahí se sigue también que
un cambio en el esquema puede cambiar cómo se construye la cadena aunque la
especificación de la huella siga diciendo lo mismo: un nuevo valor de
`TipoHuella`, otras longitudes máximas u otro tipo para un campo.

El detalle de cada punto está en [ambiguedades.md](ambiguedades.md) (puntos 5,
6, 7 y 10), y el código y los tests, en el
[repositorio](https://github.com/mshodai/validador-cadena-verifactu).

---

Este análisis es de arquitectura de software, no asesoramiento jurídico.
