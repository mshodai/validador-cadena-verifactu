---
title: "¿Qué comprueba Hacienda al recibir tus registros de facturación en un requerimiento?"
description: "Qué valida la AEAT cuando un sistema de facturación NO VERI*FACTU remite sus registros por requerimiento, qué se acepta con errores y qué no figura entre las validaciones documentadas: la comprobación del encadenamiento."
---

# ¿Qué comprueba Hacienda al recibir tus registros de facturación en un requerimiento?

Si tu sistema de facturación conserva sus propios registros y Hacienda te los
requiere, los envías a través de un servicio web de la AEAT y recibes una
respuesta. Este artículo reúne lo que dicen los documentos técnicos de la AEAT
sobre qué se comprueba en ese momento, y señala dónde no dicen nada.

Las fuentes son tres: AEAT, "Sistemas Informáticos de Facturación y Sistemas
VERI\*FACTU. Validaciones", versión 1.2.2, 08/04/2026 (en adelante,
*Validaciones*); AEAT, "Aclaraciones a dudas de los desarrolladores", versión
1.3, 04/12/2025 (en adelante, *FAQ*); y los esquemas XSD de suministro,
`SuministroInformacion.xsd` y `SuministroLR.xsd`, que no declaran versión.

## El escenario

Un sistema informático de facturación (SIF) en la modalidad NO VERI\*FACTU no
envía los registros a la AEAT a medida que los genera: los conserva. La AEAT
solo requiere registros a estos sistemas; a los VERI\*FACTU no, "por haberse
remitido en el momento de su generación a la AEAT y estar ya, por tanto, en su
poder" (FAQ, sección 18, p. 38).

Cuando llega el requerimiento, "los RF generados en su momento durante el
periodo requerido serán remitidos tal cual fueron generados, sin ninguna
alteración" (FAQ, sección 18, p. 38). Se envían con el mismo mensaje que la
remisión voluntaria, `RegFactuSistemaFacturacion` (`SuministroLR.xsd`), con un
bloque `RemisionRequerimiento` en la cabecera (`CabeceraType`, en
`SuministroInformacion.xsd`). Su campo `RefRequerimiento` es obligatorio en los
sistemas no verificables, y la referencia "deberá existir en la AEAT"
(Validaciones, sección 3.1.1.5, p. 7).

Antes de enviar no se puede corregir nada de los registros. El documento de
Validaciones lo dice expresamente: "no debe subsanar los errores relacionados
con las validaciones de negocio de los registros enviados, ya que estos
registros deben ser los que se han conservado en el sistema del obligado
tributario en el momento de su generación" (sección 4.3.2, p. 22). Si hay
errores de facturación, se corrigen por el proceso normal de facturación, que
"será siempre el que le corresponda según la normativa de facturación", "como
si no hubiera recibido ningún requerimiento" (FAQ, sección 18, p. 38).

Los documentos no dicen cuándo ni por qué se emite un requerimiento, en qué
plazo se contesta ni cómo se notifica.

## Qué valida la AEAT

El documento de Validaciones define tres tipos de validación, y la consecuencia
de las sintácticas depende de dónde se produce el error (sección 3.1, p. 6):

| Validación | Qué comprueba | Consecuencia |
|---|---|---|
| Estructural | que estén las etiquetas obligatorias del esquema | rechazo del mensaje completo |
| Sintáctica, en la cabecera | formato, longitud, obligatoriedad y valores permitidos | rechazo del mensaje completo |
| Sintáctica, en un registro | lo mismo, dentro de un registro de alta o anulación | rechazo de ese registro; los demás se siguen procesando |
| De negocio | campos cuyo contenido depende de otros | rechazo del registro |

En la remisión bajo requerimiento, la última fila cambia: "Todos los errores
provocados por validaciones de negocio se marcarán como errores admisibles para
no rechazar los registros de facturación conservados en el sistema del obligado
tributario, con la única excepción de las validaciones asociadas a la
identificación de `<NIF>` o `<IdOtro>`" (Validaciones, sección 4.3.2, p. 22). Un
error admisible no provoca el rechazo: el registro se acepta y la respuesta lo
señala como error "de tipo admisible" (sección 4.2, p. 21). En la práctica,
un registro conservado solo se rechaza si incumple el esquema o si falla la
identificación de un NIF o de un IdOtro. La FAQ lo resume en términos parecidos: el servicio
aplica "validaciones mínimas" y no rechaza los registros "a menos que incumplan
el esquema XML o no exista –si se hubiera rellenado– el NIF destinatario de la
factura en el censo" (sección 18, p. 38).

Que el esquema decida qué se rechaza tiene más alcance del que parece: es
también lo que impide que dos registros válidos compartan huella, como se
explica en
[¿Pueden dos facturas distintas tener la misma huella?](index.md), y lo que
fija varias decisiones sobre la huella que su especificación no toma, como se
explica en
[¿Basta la especificación de la huella para implementarla?](el-esquema-decide.md).

## Lo que se comprueba de la huella

Cada registro de alta lleva su propia huella y la del registro anterior. El
documento de Validaciones comprueba las dos, y ninguna con rechazo:

- **La huella del propio registro.** "Se validará que la huella o «hash»
  generado sea acorde a las especificaciones y formato detallados en el
  documento “Especificaciones técnicas para generación de la huella o «hash» de
  los registros de facturación” […]. En caso contrario, se devolverá un aviso de
  error (no generará rechazo)" (sección 3.1.3.23, p. 16). Entre los errores
  admisibles de la remisión voluntaria figura el caso de una huella "que no
  coincide con el calculado por la AEAT" (sección 4.3.1, p. 21), así que la AEAT
  la recalcula.
- **La huella del registro anterior.** Solo se comprueba su formato: "que la
  huella del encadenamiento del registro anterior cumpla el formato de salida
  del algoritmo SHA-256, siendo de 64 caracteres en hexadecimal y en
  mayúsculas. En caso contrario se devolverá un aviso de error (no generará
  rechazo)" (sección 3.1.3.18, p. 15).

La única otra comprobación documentada relacionada con la cadena es un error
admisible: que un registro se marque como primero ("PrimerRegistro" a "S")
cuando ya existen registros de ese sistema y ese obligado (sección 4.3.1,
p. 21).

Entre las validaciones que describe el documento no figura ninguna que
compruebe que la huella del registro anterior coincide con la huella del
registro que realmente le precede. Es decir, el encadenamiento en sí. Esto no
significa que la AEAT no lo compruebe: significa que no está documentado que lo
haga. El documento remite además a un listado de códigos de error publicado
aparte (sección 4.4, p. 22), que no forma parte de las fuentes de este
análisis.

Hay otra laguna relacionada. Cuando un SIF NO VERI\*FACTU detecta una huella
incorrecta en el registro anterior, guarda un registro de evento (FAQ, sección
15, p. 28). Pero el mensaje de remisión solo admite registros de alta y de
anulación (`SuministroLR.xsd`), y los documentos no dicen si los registros de
evento se remiten en un requerimiento ni cómo.

## Por qué no tiene por qué ser un descuido

Los documentos no explican por qué no se valida el encadenamiento. Pero hay una
razón que haría coherente esa ausencia con lo demás que dicen.

Una cadena con una rotura en medio puede ser legítima. La FAQ explica qué debe
hacer un SIF NO VERI\*FACTU que, al ir a generar un registro, detecta que el
anterior tiene la huella incorrecta: guardar un evento y advertir del error,
"pero será preciso generar el siguiente RF, ya que la facturación por este
motivo NUNCA debe interrumpirse" (FAQ, sección 15, pregunta 2, p. 28). Los
registros que siguen a esa rotura son, por tanto, registros que la AEAT indica
que hay que generar.

Rechazar esos registros al recibirlos iría contra ese mismo criterio y contra
el propósito que la sección 4.3.2 da a su regla, que es "no rechazar los
registros de facturación conservados en el sistema del obligado tributario".
Lo que la ausencia deja sin explicar es otra cosa: por qué no consta ni
siquiera como aviso, igual que la huella del propio registro.

## La consecuencia

El encadenamiento sí se comprueba, pero en otro sitio: en el propio SIF. Antes
de generar cada registro, el sistema debe comprobar que "el último registro de
facturación generado está correctamente encadenado" (artículo 7.i de la Orden
HAC/1177/2024, citado en la FAQ, sección 15, p. 28). Para los SIF NO
VERI\*FACTU esa comprobación "es SIEMPRE OBLIGATORIA", y además deben ofrecer
funciones de detección de anomalías que el usuario pueda lanzar "cuando el
usuario del SIF estime oportuno" (FAQ, sección 15, pregunta 5, p. 30).

Ese control lo hace el mismo sistema que generó la cadena. En la recepción, las
validaciones documentadas no incluyen el encadenamiento, y lo que se envía ya no
se puede corregir. Por tanto, la última ocasión de revisar la cadena tal como se
va a entregar, con una herramienta distinta del sistema que la generó, es antes
de enviarla. El resultado de esa revisión es un diagnóstico, no una corrección:
los registros se remiten igual.

El validador de este
[repositorio](https://github.com/mshodai/validador-cadena-verifactu) hace esa
revisión sobre los registros de alta. Recalcula la huella de cada uno (E01),
comprueba que cada registro enlaza con la huella declarada del anterior (E02) y
recorre la cadena entera sin detenerse en la primera rotura. Sus límites (no
comprueba firmas, no detecta una cadena reescrita por completo, no trata
registros de anulación ni de evento) están descritos en su README.

---

Este análisis es de arquitectura de software, no asesoramiento jurídico.
