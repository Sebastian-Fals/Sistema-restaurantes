# Stack tecnológico — Mesa

> **Estado:** decisión de arquitectura inicial, alineada con `resume.md` y el diseño de Penpot. No implica que el software ya esté implementado ni que el producto esté autorizado para procesar pagos o emitir documentos fiscales.
>
> **Producto:** plataforma web multiempresa para cafeterías colombianas, en español y COP. El MVP se centra en fidelización y compras verificadas; pedidos y cocina llegan en etapa 2. Pagos integrados, caja y facturación electrónica requieren definición y validación propias.

## Decisiones resumidas

| Área | Tecnología / decisión | Motivo |
| --- | --- | --- |
| Paquetes JavaScript | **pnpm** | Instalaciones rápidas, lockfile reproducible y soporte de workspace si el repositorio evoluciona a monorepo. |
| Paquetes Python | **uv** | Entornos, dependencias y lockfile `uv.lock` con sincronización reproducible. |
| Frontend | **Next.js App Router + React + TypeScript** | Web pública indexable y aplicación adaptable para clientes, negocios, operación y plataforma. Conserva la propuesta de `resume.md`. |
| Backend | **Django + Django REST Framework (DRF)** | Núcleo de negocio con ORM, migraciones, autenticación/permisos, administración interna y APIs explícitas. |
| Base de datos | **PostgreSQL** | Fuente de verdad relacional para operaciones concurrentes, auditoría y transacciones. |
| Cola y tareas | **Redis + Celery**, incorporarlos cuando haya trabajo asíncrono real | Correos, conciliación, documentos fiscales y reintentos no deben bloquear una petición web. |
| Diseño | **Penpot como referencia**; tokens CSS y componentes accesibles en código | Mantener la implementación alineada con el sistema visual y los flujos del archivo de diseño. |

## Gestores de paquetes

### Node.js: pnpm

- pnpm será el único gestor para dependencias JavaScript y TypeScript.
- Versionar `pnpm-lock.yaml`; fijar una versión de pnpm mediante `packageManager` en `package.json` y usar Node.js en versión LTS soportada.
- Instalar con `pnpm install --frozen-lockfile` en CI y despliegues.
- Si se comparte código entre aplicaciones, usar el workspace de pnpm (`pnpm-workspace.yaml`) en vez de duplicar paquetes.
- No mezclar npm o Yarn ni mantener lockfiles alternativos.

### Python: uv

- uv será el único gestor para dependencias, entornos y ejecución de herramientas Python.
- Declarar dependencias y rangos compatibles en `pyproject.toml`; versionar `uv.lock`.
- Usar `uv sync --locked` en CI/despliegues y `uv run ...` para ejecutar comandos dentro del entorno del proyecto.
- No editar `uv.lock` manualmente ni mantener a la vez un flujo paralelo de `pip`/`requirements.txt`, salvo exportación necesaria para una plataforma concreta.

## Backend

### Elección: Django + DRF

Django es la recomendación para el servidor principal. El producto necesita más que endpoints rápidos: requiere reglas de negocio consistentes, identidad, permisos, separación entre empresas y sedes, operaciones administrativas y un historial fiable de compras, canjes, caja y documentos. Django ofrece piezas integradas para construir y mantener ese núcleo; DRF permite exponer una API versionada para Next.js y otros clientes.

**Diseño de aplicación:** empezar como un **monolito modular**, organizado por dominios (identidad y acceso, negocios/sedes, fidelización, compras, pedidos, caja, pagos, facturación, auditoría). Mantener límites claros entre módulos y contratos de integración. No introducir microservicios hasta que una necesidad operativa medida lo justifique.

**Reglas de implementación del backend:**

1. **El servidor es la autoridad.** Validar permisos, negocio, sede y estado en cada operación; un botón oculto en la interfaz nunca protege un recurso.
2. **Aislar cada tenant en consultas y escrituras.** Toda entidad de negocio debe tener ámbito explícito de negocio y, cuando corresponda, sede. Denegar por defecto si el contexto no está autorizado.
3. **Transacciones breves y operaciones atómicas.** Compra, movimiento de caja, aplicación de puntos/sellos y canje deben actualizarse de forma coherente. Usar constraints de base de datos, bloqueos de fila cuando proceda y reintentos controlados ante conflictos.
4. **Idempotencia en escrituras sensibles.** Aceptar claves idempotentes con ámbito de negocio/operación; guardar el resultado original para que un reintento seguro no duplique cobros, compras, sellos, canjes o documentos.
5. **Libro de eventos financieros inmutable.** Registrar movimientos compensatorios para reversos y reembolsos; no editar ni borrar el historial para “corregir” dinero. Guardar actor, fecha, motivo, referencia externa y sede.
6. **Dinero como unidades menores enteras.** Guardar COP como entero (sin `float`); incluir moneda en importes y contratos. Definir reglas de redondeo antes de incorporar otros activos/monedas.
7. **Separar pedido, pago y factura.** Son ciclos de vida relacionados, pero independientes: un pedido puede prepararse antes de pagarse; un pago puede fallar sin borrar el pedido; una factura puede estar pendiente de transmisión/validación.
8. **Integraciones fiables.** Aplicar patrón outbox/eventos durables para efectos externos después del commit; procesar webhooks con firma, deduplicación, almacenamiento de eventos y reintentos. No asumir que una llamada HTTP y una transacción SQL forman una única transacción.
9. **Auditoría y observabilidad.** Logs estructurados sin secretos ni datos de tarjeta, identificador de correlación, métricas y alertas para fallas de pago, caja, canje y emisión fiscal.
10. **Seguridad por diseño.** Secretos fuera del repositorio, TLS, controles de acceso mínimos, protección CSRF donde aplique, límites de tasa, rotación de credenciales, copias de seguridad cifradas y procedimientos de restauración.

### Pagos y caja: alcance de “sistema propio”

Construir propio el **subledger operativo**: intentos y estados de pago, referencias del proveedor, asignación a pedido/compra, movimientos de caja, aperturas/cierres, arqueos, diferencias y conciliación. El MVP debe soportar registro manual o estados simulados hasta que exista una integración validada.

La captura/autorización/liquidación de dinero debe integrarse mediante **adquirente, pasarela o proveedor de pagos**. No guardar PAN completo, CVV ni credenciales de tarjeta; preferir checkout/tokenización alojados por el proveedor y conservar solo tokens o referencias permitidas. Un procesador propio o custodia de fondos amplía sustancialmente el alcance regulatorio, contractual, de seguridad y operación; no asumirlo por el nombre “pagos propios”.

El cierre de caja debe derivarse de movimientos trazables (ventas, devoluciones, entradas/salidas autorizadas y ajustes con motivo), no de un saldo editable. Conciliar los movimientos internos con los reportes del proveedor y permitir investigar diferencias sin alterar el libro original.

### Facturación electrónica colombiana

Definir una interfaz de proveedor para generación/transmisión, validación y consulta de documentos, con estados persistidos, XML/PDF o representaciones exigidas, acuses, notas crédito/débito, trazabilidad y reintentos idempotentes. Separar el documento fiscal de la compra y del pago.

Para el inicio, evaluar un **proveedor tecnológico autorizado por la DIAN** y verificar su vigencia, cobertura y contrato antes de elegirlo. Si Mesa pretende operar como proveedor tecnológico o emitir directamente para terceros, validar primero requisitos y obligaciones vigentes con asesoría contable/legal y DIAN; no tratarlo como una tarea rutinaria de programación. Las reglas y anexos técnicos cambian, por lo que se deben confirmar durante la integración.

### Datos y servicios de backend

- **PostgreSQL:** datos de identidad, tenants, catálogo, programa, compras, pedidos y subledger, con integridad referencial y restricciones únicas para prevenir duplicados.
- **Redis:** caché y broker de tareas, no fuente de verdad financiera.
- **Celery:** procesos reintentables y acotados (notificaciones, conciliación, sincronización fiscal, tareas de mantenimiento). La lógica crítica debe permanecer visible y transaccional en el dominio.
- **Archivos:** almacenamiento de objetos privado para soportes/documentos; URLs firmadas y vencimiento según política de retención.
- **API:** REST JSON versionada (`/api/v1`), validación de esquema y errores consistentes. Documentar contratos OpenAPI; no exponer secretos del servidor al navegador.

## Frontend

### Elección: Next.js App Router + React + TypeScript

Es el mejor ajuste para la propuesta actual: una misma experiencia web responsive combina páginas públicas del menú y marketing, una cuenta de cliente, administración autenticada y operación de restaurante. App Router permite renderizar páginas públicas en el servidor y reservar componentes de cliente para interacciones; React con TypeScript encaja con los componentes y capas definidos en `resume.md`.

**Reglas de estructura:**

- Separar shells y navegación para público, cliente, negocio, operación y plataforma.
- Organizar funcionalidades por dominio (`features/`), UI compartida (`shared/ui/`), tokens de diseño (`design/tokens/`), adaptadores de datos (`data/adapters/`) y autenticación/permisos.
- Usar Server Components para contenido público y lecturas aptas para servidor; marcar como Client Components solo lo que necesite estado, eventos o APIs del navegador.
- El backend Django conserva toda autorización y lógica de negocio. Las Server Actions o endpoints de Next.js pueden actuar como capa de experiencia/BFF, pero no duplicar las reglas financieras ni ser la autoridad de permisos.
- Consumir API tipada y validar en límites de entrada/salida. No enviar datos personales o secretos de proveedor a componentes públicos.
- Traducir tokens Penpot a variables CSS; usar Instrument Serif en titulares de marca y DM Sans en interfaz/datos. Mantener paleta, escala, espaciado y radios recogidos en `resume.md`.
- Diseñar mobile-first sin perder las referencias de 390, 768 y 1440 px ni el mínimo previsto de 320 px. Objetivo WCAG AA, foco visible, teclado, estados anunciados y respeto por `prefers-reduced-motion`.

**Criterio visual:** el diseño de Penpot es la referencia de interfaz, no una especificación del backend. Si una limitación técnica obliga a cambiar un flujo, documentar la diferencia y conservar los estados de carga, error, éxito, vacío y confirmación definidos para el producto.

## Arquitectura de alto nivel

```text
Navegador
  └─ Next.js (sitio público + experiencia autenticada / BFF ligero)
       └─ API REST versionada de Django + DRF
            ├─ PostgreSQL (fuente de verdad)
            ├─ Redis + Celery (tareas reintentables)
            ├─ Proveedor de pagos (adquirente/pasarela; tokenización)
            └─ Proveedor tecnológico DIAN (factura y documentos electrónicos)
```

Los proveedores externos son adaptadores reemplazables. Persistir sus identificadores y estados relevantes, pero mantener un vocabulario interno estable para evitar acoplar el dominio al formato de una empresa concreta.

## Secuencia recomendada

1. **MVP:** identidad y permisos, negocio/sede, programa de sellos, menú público, cuenta, compras verificadas, canjes, actividad, auditoría e idempotencia.
2. **Operación:** mesas, cuentas, pedidos y cocina; preparación separada del pago y sello tras confirmar el pago, de acuerdo con `resume.md`.
3. **Caja y pagos integrados:** subledger, apertura/cierre, integración con proveedor, webhooks, reembolsos y conciliación; definir procedimientos de soporte y recuperación antes de producción.
4. **Facturación electrónica:** integrar proveedor DIAN elegido, escenarios de contingencia, notas, estados y retención documental tras validar responsabilidades del producto.
5. **Crecimiento:** campañas con consentimiento, múltiples sedes y métricas ampliadas.

No adelantar microservicios, analítica pesada ni integración fiscal completa antes de confirmar el piloto y los requisitos operativos. Esta secuencia mantiene una base preparada para crecer sin atribuir al MVP funciones todavía pendientes.

## Repositorio y convenciones

- Monorepo opcional y razonable si frontend y backend comparten ciclo de cambios; usar pnpm workspace para paquetes JS/TS y uv workspace para paquetes Python solo si existen varios paquetes Python reales.
- Estructura inicial sugerida:

  ```text
  apps/
    web/                 # Next.js
    api/                 # Django + DRF
  packages/
    ui/                  # componentes/tokens compartidos si se justifican
  docs/
  ```

- No crear `packages/ui` ni un workspace Python vacío por anticipado; mantener la estructura mínima hasta que haya código compartido.
- Versionar lockfiles, migraciones, documentación de API y ejemplos de configuración sin secretos. Proveer `.env.example` con nombres y valores ficticios.
- Registrar decisiones arquitectónicas que cambien el alcance como ADRs breves en `docs/decisions/`.

## Referencias oficiales consultadas

- [Next.js App Router](https://nextjs.org/docs/app) y [Server/Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components).
- [Versiones de React](https://react.dev/versions) (la documentación consultada muestra React 19.3 como versión más reciente al momento de redactar este archivo).
- [Seguridad en Django](https://docs.djangoproject.com/en/6.0/topics/security/), [autenticación y permisos](https://docs.djangoproject.com/en/6.0/topics/auth/default/) y [transacciones de base de datos](https://docs.djangoproject.com/en/4.2/topics/db/transactions/).
- [Aislamiento de transacciones en PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html).
- [pnpm workspaces](https://pnpm.io/workspaces/) y [uv](https://docs.astral.sh/uv/) con [lockfiles](https://docs.astral.sh/uv/concepts/projects/sync/).
- [DIAN: normativa de facturación electrónica](https://micrositios.dian.gov.co/sistema-de-facturacion-electronica/normatividad/), [proveedores tecnológicos](https://micrositios.dian.gov.co/sistema-de-facturacion-electronica/proveedores-tecnologicos/) y [requisitos para facturadores electrónicos](https://micrositios.dian.gov.co/sistema-de-facturacion-electronica/requerimientos-para-ser-facturador-electronico/).

---

### Guía rápida para agentes de IA

- Leer `resume.md` antes de proponer o implementar una función; `stack.md` complementa ese alcance, no lo reemplaza.
- Tratar las etapas y decisiones pendientes de `resume.md` como límites reales. No presentar pagos integrados, facturación, caja, proximidad ni hardware como funciones ya aprobadas o implementadas.
- Aplicar permisos, aislamiento por negocio/sede, transacciones e idempotencia en el backend. No confiar en controles de interfaz.
- No borrar eventos financieros o de auditoría; corregir mediante reversos y movimientos compensatorios con motivo y actor.
- No almacenar datos completos de tarjeta ni secretos en código, logs, frontend o ejemplos.
- Antes de afirmar cumplimiento tributario o regulatorio, verificar normativa DIAN vigente y la responsabilidad concreta del producto.
- Mantener Next.js como capa web y Django como autoridad del dominio/API, salvo que un ADR aprobado documente el cambio.
- Conservar el sistema visual de Penpot y los objetivos de accesibilidad del resumen.
