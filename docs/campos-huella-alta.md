# Huella del registro de facturación de alta

Extracción hecha exclusivamente a partir de
`docs/fuentes/Veri-Factu_especificaciones_huella_hash_registros.pdf`
("Detalle de las especificaciones técnicas para generación de la huella o hash
de los registros de facturación", AEAT, versión 0.1.2, 27/08/2024, p. 1).

Las referencias "p. N" remiten a la paginación impresa del PDF ("Página: N/13"),
que coincide con la página física del fichero.

Alcance: solo el registro de facturación de **alta**. El documento también
define la huella de los registros de anulación (p. 5, p. 9, ejemplo en p. 12) y
de evento (p. 5–6, p. 9); aquí no se recogen.

---

## 1. Campos que entran en el cálculo, en orden

Fuente: p. 5, apartado 3.a ("Datos de campos a utilizar en el caso de registros
de facturación de alta (y la "ruta" de su localización dentro del registro)").

El documento dice que los campos se toman "en el orden enunciado, que coincide
con su aparición en los correspondientes diseños de registros publicados en el
anexo de la orden" (p. 5).

| Orden | Nombre del campo           | Ruta XML dentro del registro                          |
|------:|----------------------------|-------------------------------------------------------|
| 1     | `IDEmisorFactura`          | `RegistroAlta/IDFactura/IDEmisorFactura`              |
| 2     | `NumSerieFactura`          | `RegistroAlta/IDFactura/NumSerieFactura`              |
| 3     | `FechaExpedicionFactura`   | `RegistroAlta/IDFactura/FechaExpedicionFactura`       |
| 4     | `TipoFactura`              | `RegistroAlta/TipoFactura`                            |
| 5     | `CuotaTotal`               | `RegistroAlta/CuotaTotal`                             |
| 6     | `ImporteTotal`             | `RegistroAlta/ImporteTotal`                           |
| 7     | `Huella`                   | `RegistroAlta/Encadenamiento/RegistroAnterior/Huella` |
| 8     | `FechaHoraHusoGenRegistro` | `RegistroAlta/FechaHoraHusoGenRegistro`               |

Notas:

- El campo 7 (`Huella` de entrada) es la huella del **registro anterior**, dentro
  de `Encadenamiento/RegistroAnterior` (p. 5). Es distinto del campo donde se
  escribe la huella calculada del propio registro, que también se llama
  `Huella` pero está en `RegistroAlta/Huella` (p. 9).
- En el primer registro de facturación del sistema se indica `PrimerRegistro`
  con valor "S" y "no será necesario informar los campos de los bloques
  "RegistroAnterior"" (p. 9). En ese caso el campo 7 no tiene valor (p. 7 y
  p. 10, nota "(*) Sin contenido").
- El ejemplo Java de la p. 8 concatena los mismos 8 campos, con los mismos
  nombres y en el mismo orden.

---

## 2. Formato de la cadena de concatenación

Fuente: p. 6.

- Los datos se concatenan, "en el orden descrito para cada caso", "en una única
  cadena de texto con formato String" (p. 6).
- Estructura, tal como la da el documento (p. 6):

  ```
  nombreCampo1=valorCampo1&nombreCampo2=valorCampo2&nombreCampoN=valorCampoN
  ```

  (En el PDF la línea aparece partida como "nombreC / ampoN" por el ajuste de
  línea; arriba está unida.)

- Es decir: cada campo se escribe como `nombre=valor`; los pares se separan con
  `&`. Después del último par no va ningún `&`: así lo muestra la estructura
  anterior (p. 6), el ejemplo Java, que no añade separador tras
  `FechaHoraHusoGenRegistro` (p. 8), y los ejemplos (p. 10–11).
- "El nombre del campo será un valor constante tal y como se describe en el XML
  del diseño de registro" (p. 6). Los ejemplos usan el nombre del elemento, sin
  la ruta ni prefijos (por ejemplo `Huella=`, no `RegistroAnterior/Huella=`)
  (p. 10–11).

Para un registro de alta, la cadena queda así, con los nombres exactos en el
orden de la sección 1:

```
IDEmisorFactura=<v1>&NumSerieFactura=<v2>&FechaExpedicionFactura=<v3>&TipoFactura=<v4>&CuotaTotal=<v5>&ImporteTotal=<v6>&Huella=<v7>&FechaHoraHusoGenRegistro=<v8>
```

(`<vN>` es un marcador mío para el valor normalizado según la sección 3; no es
literal del documento. El esqueleto sale de la p. 6 aplicado a la lista de la
p. 5 y coincide con los ejemplos de las p. 10–11.)

---

## 3. Normalización de los valores

Fuente: p. 6–7.

### 3.1 Contenido del valor

"Los valores de los campos deberán tener la misma información contenida en el
campo correspondiente del fichero XML" (p. 6).

### 3.2 Espacios

Se eliminan "los espacios al inicio y al final de cada valor" (p. 6).

Ejemplo del documento (p. 6): si el XML contiene
`<NumSerieFactura> 12345678 / G33 </NumSerieFactura>`, "se obtendrá el valor
"12345678 / G33"". Es decir, los espacios interiores se conservan. (El párrafo
está justificado, así que no se puede saber cuántos espacios hay entre la
etiqueta y el valor. La capa de texto del PDF muestra uno a cada lado.)

El ejemplo Java aplica `valor.trim()` a cada valor (p. 8).

### 3.3 Campos ausentes o vacíos

"Si el campo no aparece en el registro (o aparece, pero sin valor), en la cadena
de caracteres solo se deberá poner el nombre del campo y el carácter "=" (sin
valor a continuación)" (p. 6).

El campo no se omite: aparece el nombre seguido de `=` y nada más.

Ejemplo del documento para alta (p. 7), primer registro sin huella anterior:

```
…ImporteTotal=123.45&Huella=&FechaHoraHusoGenRegistro=…
```

El ejemplo Java sustituye un valor `null` por la cadena vacía (p. 8).

### 3.4 Campos numéricos

Texto literal (p. 6): "en los campos numéricos se tratarán indistintamente los
valores con una o dos posiciones en los decimales, sin tener relevancia los
ceros a la derecha, considerándose todos igualmente válidos para la generación
de la huella o hash."

Ejemplo del documento (p. 6): "si el campo ImporteTotal contiene la siguiente
información: `<ImporteTotal>123.1</ImporteTotal>` se tratará correctamente, de
la misma forma que si se informara `<ImporteTotal>123.10</ImporteTotal>`."

La tabla de revisiones describe la versión 0.1.2 como "Aclaración tratamiento
de valores numéricos en el hash (ImporteTotal y/o CuotaTotal)" (p. 1).

El documento no dice qué cadena exacta hay que poner en la concatenación en
estos casos. Véase la ambigüedad 1 en [ambiguedades.md](ambiguedades.md).

---

## 4. Codificación de la cadena

"Dicha cadena de caracteres será codificada en un array de bytes en formato
UTF-8 para generar la entrada del algoritmo (o función) de huella o «hash»"
(p. 7).

El ejemplo Java obtiene los bytes con
`msg.getBytes(java.nio.charset.StandardCharsets.UTF_8)` (p. 8).

---

## 5. Algoritmo y formato de salida

### 5.1 Algoritmo

- "El algoritmo a utilizar se detalla en la Lista L12 del apartado 6 del anexo
  de la orden" (p. 4).
- "En la fecha de publicación de este documento el único algoritmo permitido es
  SHA-256" (p. 4).
- El ejemplo Java usa `MessageDigest.getInstance("SHA-256")` (p. 8).

### 5.2 Formato de la salida

Fuente: p. 9.

- "En sistema hexadecimal."
- "En mayúsculas."
- "El tamaño será de 64 caracteres alfanuméricos."

### 5.3 Dónde se escribe el resultado

- En el registro de alta, el resultado se escribe en `Huella`, ruta
  `RegistroAlta/Huella` (p. 9).
- La huella del registro "siempre ha de ir informado en el correspondiente
  campo de dicho registro", también en el primer registro de facturación
  (p. 9).

---

## 6. Vectores de prueba (registro de alta)

El documento trae tres ejemplos (p. 10–12). Dos son de alta y se transcriben
aquí. El tercero (caso 3, p. 12) es de anulación y queda fuera del alcance.

Nota de transcripción: en el PDF las cadenas y las huellas aparecen partidas en
varias líneas por el ajuste de página, a veces en mitad de un nombre o de un
valor (por ejemplo "FechaExped / icionFactura" o "01-01- / 2024"). Aquí están
unidas sin añadir ni quitar ningún carácter. Como comprobación hecha fuera del
PDF, se ha calculado el SHA-256 de cada cadena unida así (bytes UTF-8, salida
hexadecimal en mayúsculas), y en los dos casos coincide con la huella esperada
que publica el documento.

### 6.1 Caso 1: primer registro de facturación, de alta (p. 10)

Datos de entrada que da el documento (p. 10):

| # | Campo                      | Valor                       |
|--:|----------------------------|-----------------------------|
| 1 | `IDEmisorFactura`          | `89890001K`                 |
| 2 | `NumSerieFactura`          | `12345678/G33`              |
| 3 | `FechaExpedicionFactura`   | `01-01-2024`                |
| 4 | `TipoFactura`              | `F1`                        |
| 5 | `CuotaTotal`               | `12.35`                     |
| 6 | `ImporteTotal`             | `123.45`                    |
| 7 | `Huella` (*)               | *(vacío)*                   |
| 8 | `FechaHoraHusoGenRegistro` | `2024-01-01T19:20:30+01:00` |

"(*) Sin contenido, al tratarse del primer registro de ese SIF y, por tanto, no
haber registro de facturación anterior." (p. 10)

Cadena de entrada (p. 10):

```
IDEmisorFactura=89890001K&NumSerieFactura=12345678/G33&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35&ImporteTotal=123.45&Huella=&FechaHoraHusoGenRegistro=2024-01-01T19:20:30+01:00
```

Llamada tal como aparece en el documento (p. 10). La comilla de apertura es
recta (`"`) y la de cierre es tipográfica (`”`):

```
calcularHuella("IDEmisorFactura=89890001K&NumSerieFactura=12345678/G33&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35&ImporteTotal=123.45&Huella=&FechaHoraHusoGenRegistro=2024-01-01T19:20:30+01:00”);
```

Huella esperada (p. 10):

```
3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60
```

### 6.2 Caso 2: registro de alta con registro anterior en el SIF (p. 11)

Datos de entrada que da el documento (p. 11):

| # | Campo                      | Valor                                                              |
|--:|----------------------------|--------------------------------------------------------------------|
| 1 | `IDEmisorFactura`          | `89890001K`                                                        |
| 2 | `NumSerieFactura`          | `12345679/G34`                                                     |
| 3 | `FechaExpedicionFactura`   | `01-01-2024`                                                       |
| 4 | `TipoFactura`              | `F1`                                                               |
| 5 | `CuotaTotal`               | `12.35`                                                            |
| 6 | `ImporteTotal`             | `123.45`                                                           |
| 7 | `Huella`                   | `3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60` |
| 8 | `FechaHoraHusoGenRegistro` | `2024-01-01T19:20:35+01:00`                                        |

El valor de `Huella` de entrada del caso 2 es la huella esperada del caso 1
(p. 10–11).

Cadena de entrada (p. 11):

```
IDEmisorFactura=89890001K&NumSerieFactura=12345679/G34&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35&ImporteTotal=123.45&Huella=3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60&FechaHoraHusoGenRegistro=2024-01-01T19:20:35+01:00
```

Llamada tal como aparece en el documento (p. 11), con la misma mezcla de
comillas (`"` al abrir, `”` al cerrar):

```
calcularHuella("IDEmisorFactura=89890001K&NumSerieFactura=12345679/G34&FechaExpedicionFactura=01-01-2024&TipoFactura=F1&CuotaTotal=12.35&ImporteTotal=123.45&Huella=3C464DAF61ACB827C65FDA19F352A4E3BDC2C640E9E9FC4CC058073F38F12F60&FechaHoraHusoGenRegistro=2024-01-01T19:20:35+01:00”);
```

Huella esperada (p. 11):

```
F7B94CFD8924EDFF273501B01EE5153E4CE8F259766F88CF6ACB8935802A2B97
```

---

## Ambigüedades detectadas

Se han trasladado a [ambiguedades.md](ambiguedades.md), junto con lo que hace
esta implementación en cada caso.
