# Fuentes normativas

## Especificaciones de la huella (hash)
- Documento: Detalle de las especificaciones técnicas para generación
  de la huella o hash de los registros de facturación
- Autor: AEAT, Departamento de Informática Tributaria
- Versión: 0.1.2
- Fecha del documento: 27/08/2024
- Descargado: 14/09/2026
- URL: https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Veri-Factu_especificaciones_huella_hash_registros.pdf
- Nota: la página de la sede indica "actualizada 26/03/2026", pero el
  documento sigue siendo la 0.1.2. Su introducción cita "la Orden XXXXXXX",
  placeholder sin resolver, por lo que es anterior a la orden definitiva.

## Validaciones
- Documento: Sistemas Informáticos de Facturación y Sistemas VERI\*FACTU.
  Validaciones
- Autor: AEAT, Departamento de Informática Tributaria, Subdirección General
  Aplicaciones
- Versión: 1.2.2
- Fecha del documento: 08/04/2026
- Descargado: 15/09/2026
- URL: https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Validaciones_Errores_Veri-Factu.pdf
- Nota: la restricción de caracteres de NumSerieFactura está en la sección
  3.1.3.1 (p. 8). Se introdujo en la versión 1.1.3 (09/09/2025) para todos los
  campos alfanuméricos de texto libre, y desde la 1.1.4 (23/09/2025) se aplica
  solo a IDFactura.

## Esquemas XSD de suministro
- Documentos: SuministroInformacion.xsd y SuministroLR.xsd
- Autor: AEAT
- Versión: los esquemas no declaran versión ni fecha. Como fecha se indica la
  de la cabecera Last-Modified del servidor.
- SuministroInformacion.xsd
  - Fecha (Last-Modified): 11/01/2026 23:01 UTC
  - URL: https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd
- SuministroLR.xsd
  - Fecha (Last-Modified): 01/10/2025 08:07 UTC
  - URL: https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroLR.xsd
- Descargado: 15/09/2026 (guardados localmente con extensión .xsd.xml;
  idénticos byte a byte a los publicados en esas URL)
- Nota: los tipos de los campos que entran en la huella, citados en la
  ambigüedad 7 de docs/ambiguedades.md, están en SuministroInformacion.xsd.

## Preguntas frecuentes de empresas de desarrollo
- Autor: AEAT
- Actualizado: 04/12/2025 (según la sede)
- Descargado: 14/09/2026
- URL: https://sede.agenciatributaria.gob.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/FAQs-Desarrolladores.pdf

## Huellas SHA-256

Sirven para comprobar que una copia local es la misma versión con la que se hizo el análisis. Se calcularon el 22/09/2026 sobre las copias locales, descargadas en las fechas indicadas en cada sección. Una huella distinta indica un fichero distinto.

```
f4334c254bb875b417247b54315199f89d75a8c4814dfd1e86efec562653d7de  Veri-Factu_especificaciones_huella_hash_registros.pdf
426eb926fc098a36a163f66ca5f40d9e0847ca23300bbe5008979832d3513440  Validaciones_Errores_Veri-Factu.pdf
ee4c1655175644de44c4c25055ffeb8e5f4bb4bc3834ce8254d4222ef18c8aa1  SuministroInformacion.xsd.xml
cbdac8d427cc5ab5d77ca48974cab0f35d6bb819c4c66db361681e3710aeba36  SuministroLR.xsd.xml
73906dc8afbbb9da35f6cb489980352b42aed66d48828fd62a00168883c09d5e  FAQs-Desarrolladores.pdf
```

Para comprobarlas: `cd docs/fuentes && shasum -a 256 -c` pegando el bloque anterior en la entrada estándar.

## Datos para la vigilancia automática

Repite en formato legible por máquina el fichero, la URL de descarga y la huella SHA-256 de cada documento de las secciones anteriores. Lo lee el script de `vigilancia-fuentes`, que comprueba que coincida con el texto. Si difieren, prevalece el texto.

```json
{
  "documentos": [
    {
      "fichero": "Veri-Factu_especificaciones_huella_hash_registros.pdf",
      "url": "https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Veri-Factu_especificaciones_huella_hash_registros.pdf",
      "sha256": "f4334c254bb875b417247b54315199f89d75a8c4814dfd1e86efec562653d7de"
    },
    {
      "fichero": "Validaciones_Errores_Veri-Factu.pdf",
      "url": "https://www.agenciatributaria.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/Validaciones_Errores_Veri-Factu.pdf",
      "sha256": "426eb926fc098a36a163f66ca5f40d9e0847ca23300bbe5008979832d3513440"
    },
    {
      "fichero": "SuministroInformacion.xsd.xml",
      "url": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd",
      "sha256": "ee4c1655175644de44c4c25055ffeb8e5f4bb4bc3834ce8254d4222ef18c8aa1"
    },
    {
      "fichero": "SuministroLR.xsd.xml",
      "url": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroLR.xsd",
      "sha256": "cbdac8d427cc5ab5d77ca48974cab0f35d6bb819c4c66db361681e3710aeba36"
    },
    {
      "fichero": "FAQs-Desarrolladores.pdf",
      "url": "https://sede.agenciatributaria.gob.es/static_files/AEAT_Desarrolladores/EEDD/IVA/VERI-FACTU/FAQs-Desarrolladores.pdf",
      "sha256": "73906dc8afbbb9da35f6cb489980352b42aed66d48828fd62a00168883c09d5e"
    }
  ]
}
```
