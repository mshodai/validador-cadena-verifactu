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
