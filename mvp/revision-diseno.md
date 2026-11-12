# Revisión de diseño y alcance del piloto

Revisión realizada el 11 de noviembre de 2026 mediante el MCP de Penpot, sobre el archivo conectado. No se modificó el archivo de diseño.

## Referencias inspeccionadas

- `01 · Sistema visual`: board `a2455985-7d2b-80e1-8008-ed02b2fa5e1e`, fundamentos, tipografía, colores, controles y adaptación.
- `03 · Cliente · web móvil`: boards Café Olivo, acceso, tarjetas, código de cliente, recompensa, cuenta y eliminación. Se exportó y revisó visualmente Tu tarjeta (`a2455985-7d2b-80e1-8008-ed0310e0b14e`).
- `05 · Administración · MVP`: se exportó y revisó Hoy en Café Olivo (`a2455985-7d2b-80e1-8008-ed03a45cdff3`), y se inspeccionaron los nombres y alcance de los boards de compras/canjes, confirmaciones y detalle.
- `09 · Estados y accesibilidad`: contrato `a2455985-7d2b-80e1-8008-ed0669b0578e` y estados de desconexión, compra duplicada, recompensa usada/vencida, permisos y carga.

## Decisiones aplicadas

Se conserva la identidad existente: bosque `#234D3C`, tinta `#202D28`, crema `#F7F6F2`, papel blanco, salvia `#EAF0E7`, lima `#DCEBA9`, terracota `#B75232` y error `#A43832`. Instrument Serif identifica la marca; DM Sans se usa para tareas, navegación y datos.

El panel mantiene sidebar clara, métricas separadas por divisores y bloque del programa en salvia. Se amplía a seis métricas para incluir compras y recompensas disponibles y se agrega periodo seleccionable. Los datos se obtienen de la API, sin copiar cifras de muestra del diseño.

Las tarjetas mantienen fondo bosque y sellos lima. Se ajustan encabezados de tareas a DM Sans, jerarquía de títulos del menú y textos de lectura a 16 px. Se mantiene la adaptación móvil en vez de copiar tamaños fijos de los boards.

Los fallos de conexión mantienen los datos ingresados y liberan los controles. Ante una compra de resultado incierto se conserva la referencia para reintentar sin duplicar. El canje vuelve a consultar las recompensas disponibles y el reverso reconcilia su estado antes de ofrecer reintento. Se conservan confirmaciones sensibles, etiquetas, foco visible, Escape y retorno de foco de diálogos, y se incorpora enlace para saltar al contenido.

## Diferencias intencionales respecto de Penpot

`mvp/alcance.md` es la autoridad funcional. El diseño incluye pedidos/cocina, campañas, varias sedes, onboarding completo y administración avanzada. Esas opciones no se agregan al menú ni se implementan para este piloto. Configuración de negocio, menú, programa y personal continúa en las herramientas internas de Django.

Los valores, fechas y negocios del diseño son ejemplos. La demostración usa datos sintéticos y el piloto debe configurar sus propias condiciones y contacto. No se promete que la app procesa pagos ni verifica el POS.

La página pública es una herramienta de consulta de menú y fidelización. Las reglas genéricas de landing pages que exigen un hero de pantalla completa, efectos, fotografías o botones de compra por producto no se aplican: introducirlas alteraría el diseño y el alcance acordados. Los resultados de esos checkers se distinguen de las comprobaciones funcionales y de accesibilidad.

## Evidencia y límites

Se inspeccionó una captura real de la página pública a 390 px y se comparó con los boards y tokens de Penpot. Las pruebas Playwright verifican reglas públicas entre 320 y 1440 px, los recorridos de cliente/personal/administración, foco del diálogo y recuperación de respuestas perdidas. No se afirma igualdad píxel a píxel ni una certificación completa con lectores de pantalla o dispositivos físicos.

Las superficies nuevas o ampliadas siguen el modo de operación: claridad, lectura y controles reconocibles. La revisión no convierte el prototipo en una landing de marketing ni introduce funciones futuras.

La última ejecución del checker genérico sobre la compilación de producción devolvió `GATE: FAIL 20
(round 2 of 3)`. Sus hallazgos pendientes se refieren a hero y secciones de pantalla completa, efectos,
fotografías/visuales, CTA por sección, clases `.wrap`, alineaciones de una landing, tamaños iguales para
todos los H3 y contraste de cuerpo 7:1. No se afirma que ese gate pase: esas reglas difieren del menú
operativo y del contrato de Penpot (contraste normal mínimo 4,5:1; el texto atenuado medido fue 4,7:1).
No se agregaron exenciones para ocultar los hallazgos. Los avisos genéricos incluyen navegación,
encabezados/copy, cantidad de acciones, separación de secciones y metadatos de compartir; el contenido,
los controles, las medidas y las superficies del producto se validan con las pruebas y referencias
anteriores. La primera pasada había observado un HTTP 500 durante el reinicio de la API; la página
de producción posterior respondió HTTP 200 y el checker ya no reportó un fallo de carga.
