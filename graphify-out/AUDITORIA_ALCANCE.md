# Revisión del MVP frente a mvp/alcance.md

Fecha: 2026-11-11. Revisión del código y pruebas locales; no se modificó la implementación.

## Dictamen

La implementación sigue el producto y los límites del alcance: hay un recorrido de fidelización con configuración interna, página pública, acceso por correo, tarjeta, compras, canjes y administración. No encontré ampliaciones hacia pagos, POS, DIAN, pedidos, cocina, campañas o varias sedes.

Todavía no cumple por completo lo necesario para cerrar la aceptación del piloto. El principal defecto confirmado es el reverso de compras antiguas que contribuyeron a una recompensa ya canjeada. Además faltan controles y métricas del resumen y completar algunos estados de error.

## Cobertura de los seis flujos

| Flujo del alcance §4 | Evidencia | Estado |
| --- | --- | --- |
| Descubrir | `apps/web/src/app/b/[slug]/page.tsx`: menú, categorías, disponibilidad, precios COP y reglas previas al registro | Implementado; móvil y escritorio requieren aceptación en navegador |
| Activar tarjeta | Acceso por código, `ActivateCard`, tarjeta vacía e idempotencia de activación | Implementado y cubierto parcialmente por pruebas; correo real no verificado |
| Comprar y acreditar | Personal autorizado, mínimo configurable, un sello, referencia única por negocio, actor y fecha | Implementado; reintento secuencial probado; ver límite de idempotencia abajo |
| Completar y canjear | Emisión de recompensa, vencimiento y bloqueo de consumo repetido; confirmación asistida en pantalla | Implementado; el segundo intento devuelve conflicto, sin segundo consumo |
| Administrar | Resumen, actividad con filtros, detalle y actor | Parcial: faltan periodo seleccionable y recompensas disponibles en el resumen |
| Corregir un error | Reverso con motivo y registro separado, sin borrar compra | Parcial: falla el escalamiento a soporte en el caso reproducido abajo |

La dirección del negocio representa la única sede. No es necesario agregar gestión de múltiples sedes ni autoservicio para cumplir este alcance. El QR puede entregarse como material de incorporación: el alcance no exige un generador dentro de la aplicación.

## Hallazgos

### 1. Alta: reversar una compra antigua puede descontar sellos de un ciclo nuevo

Requisito: alcance §4.6, línea 100: si la recompensa derivada ya fue usada, escalar a soporte.

Evidencia: `apps/api/mesa/loyalty/domain.py:90` y `apps/api/mesa/loyalty/use_cases.py:68`.

Reproducción en base SQLite en memoria, sin tocar los datos de la demo:

1. Programa de 3 sellos; registrar compras T-0, T-1 y T-2.
2. Canjear la recompensa generada por T-2.
3. Registrar T-new: queda un sello del siguiente ciclo.
4. Reversar T-0.

Resultado observado: se acepta el reverso, se descuenta el sello del ciclo nuevo y la recompensa anterior sigue canjeada. Debía devolverse `needs_support`. El atajo `elif stamps > 0` no identifica a qué ciclo perteneció el sello. La prueba existente solo verifica el reverso de la compra que completó la recompensa.

### 2. Media: resumen del negocio incompleto

Requisito: alcance §3.6, líneas 85–89: compras y sellos en un periodo seleccionable; recompensas disponibles y canjeadas.

Evidencia: `apps/web/src/app/app/[slug]/page.tsx:19` y `:39`; `apps/api/mesa/loyalty/selectors.py:23`.

El backend admite `start`/`end` y calcula `purchases` y `rewards_available`. El frontend llama al resumen sin filtros, fija el texto a últimos 30 días y no presenta esas dos métricas. Los filtros de la pantalla Actividad sí existen, pero no cambian el resumen.

### 3. Media: fallos de red sin recuperación en el panel

Requisito: alcance §7, línea 144: estados de carga, error y éxito comprensibles.

Evidencia: `apps/web/src/app/app/[slug]/compras/page.tsx:67` y `:104`.

Las acciones de registrar compra y canjear fijan `busy=true`, esperan la petición y luego restablecen el estado; no hay `catch/finally`. Si fetch rechaza por un fallo de red, no se llega al restablecimiento y los controles pueden permanecer deshabilitados. También faltan capturas de rechazo en algunas lecturas del resumen y actividad. Hallazgo por inspección de código; no se simuló desconexión en navegador.

### 4. Media: reintentos de compra condicionados al estado actual del programa

Requisito: alcance §3.4: repetir la referencia devuelve el resultado existente.

Evidencia: `apps/api/mesa/loyalty/use_cases.py:28`.

Reproducción confirmada: registrar una compra, desactivar el programa y reenviar idéntica compra con la misma referencia. Devuelve `no_active_program`, aunque ya existe la operación. No duplica el sello, pero no devuelve el resultado original como exige el alcance. La validación de programa activo precede la búsqueda de la referencia.

### 5. Pendiente de completar: retención de correos tras eliminación

Requisitos relacionados: alcance §3.3 y §6, minimización y eliminación sujeta a registros conservados.

Evidencia: `apps/api/mesa/loyalty/adapters/orm.py:102` y `apps/api/mesa/identity/models.py:31`.

La eliminación anonimiza `User`, desactiva la cuenta y elimina consentimientos; conserva las operaciones como corresponde. Reproduje que `LoginCode.email` mantiene el correo original. No encontré una limpieza/retención de códigos en el código revisado. Debe definirse qué historial de acceso se necesita conservar y eliminar o anonimizar lo restante. Es una observación técnica, no una conclusión normativa.

## Aceptación aún no verificada

- Operación real a 320 px, navegación completa con teclado y todos los estados en navegador. Hay CSS adaptable, etiquetas y manejo de foco, pero no constituyen por sí solos una prueba de aceptación.
- Concurrencia en PostgreSQL para compras, canjes y reversos. Las pruebas locales usan SQLite en memoria y no acreditan por sí solas el comportamiento de bloqueos en PostgreSQL.
- Entrega real de códigos por correo. Existe adaptador Resend; la sesión de revisión ejecuta consola de desarrollo.
- Incorporación real de un negocio: `mvp/piloto.md` proporciona instrucciones y límites, pero el canal de soporte y las condiciones de continuación deben acordarse y comprobarse antes de activar el piloto.
- Indicadores del §10: hay compras, clientes, retornos y recompensas; visitas, rechazos/duplicados y tiempos de soporte no tienen instrumentación específica observada. Pueden registrarse manualmente durante el piloto si así se acuerda; no requieren analítica avanzada.

## Verificación realizada

- `apps/api/.venv/bin/python -m pytest -q`: **38 passed**.
- `pnpm typecheck` en `apps/web`: **correcto**.
- Reproducciones adicionales aisladas en SQLite en memoria: reverso de un sello de ciclo anterior, reintento tras desactivar programa y correo persistente en LoginCode tras eliminar cuenta.
- No se probó el despliegue productivo ni se realizó auditoría visual o comparación de fidelidad con Penpot.

Prioridad sugerida: corregir reversos y agregar su prueba de regresión; completar resumen; cerrar errores de red e idempotencia; definir limpieza de accesos y ejecutar aceptación móvil/teclado y concurrencia antes de ofrecerlo a clientes reales.
