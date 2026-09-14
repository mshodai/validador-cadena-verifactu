# 0001. Validar cadenas de registros en lugar de emitirlos

- Estado: aceptada
- Fecha: 15/09/2026

## Contexto

Desde la Ley 11/2021, de medidas de prevención y lucha contra el fraude fiscal,
el artículo 29.2.j) de la Ley General Tributaria obliga a productores,
comercializadores y usuarios de los programas que soportan la facturación a que
estos "garanticen la integridad, conservación, accesibilidad, legibilidad,
trazabilidad e inalterabilidad de los registros, sin interpolaciones, omisiones
o alteraciones de las que no quede la debida anotación en los sistemas mismos".
El preámbulo de la ley lo justifica "con el objetivo de no permitir la
producción y tenencia de programas y sistemas informáticos que permitan la
manipulación de los datos contables y de gestión". El Reglamento aprobado por el Real Decreto 1007/2023 desarrolla
esa obligación para los sistemas informáticos de facturación (SIF), y la Orden
HAC/1177/2024 fija sus especificaciones técnicas. El calendario de
obligatoriedad está en el [README](../../README.md#fuentes).

El mecanismo central es la huella. Cada registro de facturación incluye un
SHA-256 calculado sobre algunos de sus campos y sobre la huella del registro
anterior, de modo que los registros forman una cadena. Si un registro se
altera, se pierde, se añade o cambia de orden, la cadena deja de cuadrar en ese
punto, salvo que se recalculen todas las huellas posteriores.

Un SIF puede funcionar en dos modalidades. En la modalidad VERI\*FACTU remite
cada registro a la AEAT en el momento de generarlo. En la modalidad NO
VERI\*FACTU los conserva él mismo, firmados electrónicamente, y solo los remite
si la AEAT los requiere. En ese caso, según las preguntas frecuentes de la AEAT
para desarrolladores, los registros "serán remitidos tal cual fueron generados,
sin ninguna alteración", y el servicio web que los recibe aplica "validaciones
mínimas": no los rechaza salvo que incumplan el esquema XML o que el NIF del
destinatario no exista en el censo (FAQ, versión 1.3, sección 18, p. 38).

Por tanto, quien responde a un requerimiento no puede corregir su cadena antes
de enviarla, y el envío tampoco le dice si está íntegra. El problema que aborda
este proyecto es saberlo antes, a partir de los registros tal como están.

## Decisión

Este proyecto valida cadenas de registros ya generados; no emite registros.
Recibe una secuencia ordenada de registros de alta, recalcula la huella de cada
uno según la especificación de la AEAT y comprueba el encadenamiento. No
expide facturas, no genera ni firma registros y no remite nada.

Hay dos razones.

**Un emisor elige; un validador no sabe qué se eligió.** La especificación de
la huella deja abiertos puntos que cambian el resultado: si `123.1` y `123.10`
dan la misma huella, qué caracteres se recortan de los extremos de cada valor o
qué hacer si un valor contiene `&` o `=`. Para un emisor, cada punto es una
decisión que se toma una vez: elige una interpretación, la aplica siempre igual
y sigue adelante, y sus registros son coherentes consigo mismos. Un validador
recibe registros de un emisor cuya elección desconoce, y cualquier diferencia
de interpretación aparece como una huella que no cuadra. Es en la validación
donde las ambigüedades tienen consecuencias y hay que tratarlas de forma
explícita. Un emisor más no aporta nada a ese problema.

**Publicar un emisor plantea si el artefacto es un SIF.** El Reglamento define
el SIF como el "conjunto de hardware y software utilizado para expedir
facturas" mediante tres acciones: admitir la entrada de información de
facturación, conservarla y procesarla "para producir otros resultados
derivados" (art. 1.2). Un programa que genera registros de facturación
encadenados forma parte de ese conjunto, y publicarlo abriría la cuestión de si
es un SIF sujeto al Reglamento, con los requisitos que eso conlleva. Una
herramienta que solo lee registros ya generados y comprueba sus huellas no se
usa para expedir facturas. Es cierto que procesa información de facturación,
pero la definición se refiere al conjunto utilizado para expedirlas, y esta
herramienta no interviene en la expedición. Esta es la lectura del proyecto, no
un dictamen jurídico.

## Consecuencias

**El validador recorre la cadena entera y no se detiene en el primer fallo.**
La AEAT indica que, si un SIF NO VERI\*FACTU detecta que el registro anterior
tiene la huella incorrecta, debe guardar un evento y advertir del error, "pero
será preciso generar el siguiente RF, ya que la facturación por este motivo
NUNCA debe interrumpirse" (FAQ, versión 1.3, sección 15, pregunta 2, p. 28).
Existen, por tanto, cadenas legítimas con roturas en medio y registros válidos
después. Un validador que abortara en la primera incidencia ocultaría el estado
del resto.

Por la misma razón, E02 compara el campo `Huella` de cada registro con la huella
declarada del anterior, no con la recalculada. El SIF encadena cada registro
nuevo anotando en él la huella que figura en el anterior (FAQ, sección 15,
p. 28), así que una rotura aparece como una incidencia localizada y no se
arrastra a todos los registros siguientes. El corpus
[`fixtures/cadena-rota.json`](../../fixtures/cadena-rota.json) contiene una
rotura de cada tipo en medio de una cadena válida.

**Las ambigüedades de la especificación se convierten en decisiones explícitas
y documentadas.** Como el validador no sabe qué interpretación eligió el
emisor, no resuelve ninguna. En cada punto hace lo mínimo que reproduce los
vectores oficiales, lo señala en el código con un comentario `# AMBIGÜEDAD:` y
lo documenta en [docs/ambiguedades.md](../ambiguedades.md), con lo que hace y a
quién afecta. Esto cambia cómo se lee un E01: significa que la huella no cuadra
según esas decisiones, y puede deberse a una alteración o a que el emisor
interpretó un punto de otra forma. El mismo documento recoge las decisiones que
no proceden de la especificación, sino del propio acto de validar, como la
forma de comparar las huellas.

**Hay límites que el validador no puede cubrir.**

- **Una cadena reescrita por completo.** Si alguien altera un registro y
  recalcula su huella y todas las posteriores, la validación pasa sin
  incidencias. Esa garantía la aportan la firma electrónica de los registros en
  la modalidad NO VERI\*FACTU y la remisión inmediata a la AEAT en la modalidad
  VERI\*FACTU. El validador no comprueba firmas ni tiene acceso a lo que la AEAT
  ha recibido.
- **Un tramo parcial de cadena.** El validador trata el primer registro de la
  lista como el primero del sistema. Si el tramo no empieza en el origen, su
  primer registro da E02 aunque no haya rotura.
- **Lo que no llega al validador.** Solo trata registros de alta, y recibe los
  valores ya extraídos del XML. Cómo se extraen puede cambiar la huella
  (ambigüedades 5 y 6 de [docs/ambiguedades.md](../ambiguedades.md)).
- **Informar no es reparar.** Como los registros se remiten tal cual fueron
  generados, el resultado de la validación es un diagnóstico, no una
  corrección.

## Referencias

- Ley 58/2003, General Tributaria, art. 29.2.j), añadido por el art. 13.4 de la
  Ley 11/2021, de 9 de julio:
  <https://www.boe.es/buscar/act.php?id=BOE-A-2003-23186>
- Real Decreto 1007/2023, de 5 de diciembre, y Reglamento que aprueba:
  <https://www.boe.es/buscar/act.php?id=BOE-A-2023-24840>
- AEAT, "Aclaraciones a dudas de los desarrolladores", versión 1.3,
  4 de diciembre de 2025:
  <https://sede.agenciatributaria.gob.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/FAQs-Desarrolladores.pdf>
- AEAT, "Detalle de las especificaciones técnicas para generación de la huella
  o hash de los registros de facturación", versión 0.1.2, 27/08/2024:
  <https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Veri-Factu_especificaciones_huella_hash_registros.pdf>
