# resume.md — Plataforma de restaurantes, UI/UX v0.1
Fecha: 10 de noviembre de 2026. Resumen exportado desde Penpot al directorio del proyecto por solicitud del propietario.

## Producto y alcance
Mesa es una etiqueta de trabajo, no el nombre comercial. Contexto aprobado: cafeterías colombianas, español y COP. Café Olivo y todos los datos del diseño son sintéticos.
MVP: alta de negocio, un programa de sellos, menú público, cuenta y colección del cliente, compras verificadas, canjes, actividad y permisos.
Etapa 2: mesas, cuentas, pedidos de personal y clientes, cocina/barra, preparación separada del pago y sello automático tras confirmar pago.
Futuro: campañas, varias sedes y métricas ampliadas. Proximidad, caja, pagos integrados, fiscalidad, inventario y hardware requieren validación propia.

## Dirección visual
Paleta: bosque #234D3C; tinta #202D28; fondo crema #F7F6F2; papel #FFFFFF; salvia #EAF0E7; lima #DCEBA9; terracota #B75232; borde #DCE1D9; secundario #65716B; error #A43832.
Instrument Serif para marca y titulares comerciales. DM Sans para interfaz y datos. Escala 72/60/48 en narrativa; 34/30/24/20/16/14/12 en operación.
Base espacial 4px; ritmo 8,16,24,32,48,64. Radio 8 controles, 16 tarjetas. Botones 48px, áreas táctiles mínimas 44px. Iconos vectoriales 1,7px. Sin gradientes.
Superficies claras para trabajar durante el servicio. Verde para acciones y tarjeta, lima para progreso. El color nunca es la única señal de estado.

## UX y reglas de negocio
Menú sin registro. Cuenta por código de correo como hipótesis inicial; misma ruta para recuperación. Consentimiento comercial separado por negocio y canal, opcional y revocable.
Un sello por compra pagada y elegible. Ejemplo: compra mínima COP 12.000, 10 sellos, americano mediano, recompensa válida 30 días. Son reglas de demostración, configurables por negocio.
QR público solo identifica negocio o mesa. Código personal identifica cliente; nunca prueba compra. La escritura exige rol autorizado.
Compra y evento de fidelización con claves de idempotencia por establecimiento; referencia única y comprobación final antes de acreditar. Reintento muestra resultado original.
Canje con código temporal, sede, vigencia y estado comprobados de nuevo al confirmar. Consumo atómico de una recompensa.
Reembolso crea reversión; no borra eventos. Si una recompensa derivada ya fue consumida, revisión del administrador. Ajustes con motivo, actor, sede y fecha.
Preparación: pendiente de aceptación, confirmado, en preparación, listo, entregado o cancelado. Pago: pendiente, pagado o reembolsado, independiente.
Mesa agrupa cuentas; cada cuenta agrupa pedidos. Separación mediante cuentas identificadas; división avanzada y pagos parciales fuera de alcance inicial.
Sesión de mesa acotada a la visita; envío idempotente, aceptación del personal y opción de revisar cuando la sesión vence.

## Estructura del frontend propuesta
Web adaptable. Stack propuesto, no implementado: React + TypeScript, renderizado público con Next.js, componentes accesibles y tokens CSS. La elección final requiere validar arquitectura y despliegue.
Grupos de rutas:
marketing: /, /piloto, /como-funciona
public: /b/:slug/menu, /b/:slug/programa, /mesa/:token
identity: /acceso, /verificar, /invitacion/:token
customer: /mis-tarjetas, /tarjeta/:id, /recompensa/:id, /cuenta, /privacidad
onboarding: /alta/negocio, /alta/programa, /alta/menu, /alta/revision
merchant: /app/:businessId/resumen, /programa, /clientes, /compras, /canjes, /menu, /equipo, /configuracion
operations: /operacion/:branchId/mesas, /pedidos/:id, /cocina
growth: /campanas, /sedes, /metricas
platform: /plataforma/negocios, /suscripciones, /soporte, /auditoria
Capas: app/routing; features por dominio; shared/ui; design/tokens; data/adapters; auth/permissions. Separar shell público, cliente, negocio, operación y plataforma.
Componentes: Button, Field, Select, Checkbox, StatusBadge, LoyaltyCard, StampGrid, DataTable, EmptyState, Feedback, ConfirmationDialog, OrderTicket, TableTile y ResponsiveShell.
El servidor aplica permisos, aislamiento de negocio/sede, transacciones e idempotencia; ocultar un botón no constituye seguridad.

## Adaptación y accesibilidad
Referencias 1440 escritorio, 768 tableta y 390 móvil. Mínimo previsto 320px. Sidebar se convierte en menú; tablas en filas con detalle. Cliente usa navegación inferior. Cocina prioriza tamaño de texto y modificadores.
Objetivo WCAG AA: texto normal 4,5:1, grande 3:1; foco visible; navegación por teclado; errores anunciados; retorno de foco en diálogos; zoom 200%; mensajes de estado. Verificación funcional pendiente de implementación.
Animación propuesta: entrada única del hero 240ms, respuesta de botones 120ms y sello nuevo 180ms; respetar reduced-motion.

## Métricas
Distinguir inscritos, tarjetas activas, sellos, recompensas obtenidas/canjeadas, compras y pedidos. Recurrencia observada: clientes con dos o más compras del periodo. No prometer causalidad de campañas.
Pedido medio: total de pedidos pagados dividido por pedidos pagados. Evitar contar dos veces una compra registrada también como pedido.

## Referencias y criterio
Square Loyalty — https://squareup.com/us/en/software/loyalty : relación entre compra, recompensa y actividad; usar trazabilidad, no copiar marca ni estadísticas.
Loopy Loyalty — https://loopyloyalty.com/ : tarjeta y progreso reconocibles; adaptar a cuenta web compartida. No prometer integración con Wallet.
Toast KDS — https://pos.toasttab.com/hardware/kitchen-display-system : prioridad de comandas, modificadores y tiempos; mantener cobro fuera de cocina.
Fivestars — https://fsweb.fivestars.com/products/loyalty-retention/ : continuidad entre inscripción y retorno; marketing siempre con consentimiento.
Búsqueda de nombres encontró Vuelta, Vuelve y Mesalia ya en productos cercanos; no adoptarlos. Mesa permanece como rótulo descriptivo interno, sin verificación marcaria.

## Entrega y límites
Todo está en el archivo Penpot Sistema de restaurantes. Capas editables y recorridos dentro de cada página. En este prototipo, la API rechazó navigate-to entre páginas: saltos de contexto se anotan como destino de implementación.
Los códigos QR son símbolos de maqueta, no códigos utilizables. Formularios, pagos, envíos y validaciones son estados de prototipo; no ejecutan operaciones reales.
Este archivo físico se basa en el contenido original guardado en Penpot. Todavía no se han implementado frontend, backend ni despliegue.
Decisiones pendientes: nombre, método de identidad validado, reglas comerciales, precio y duración del piloto, textos de privacidad, proveedores, política detallada de devoluciones, pedidos esenciales para primeros compradores y compatibilidad de proximidad.

## Enlaces de diseño

- [00 · Guía y alcance](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/275e4692-9a43-8087-8008-ecfe91b8bf70)
- [01 · Sistema visual](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed023699210c)
- [02 · Landing y ventas](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed023699a2b8)
- [03 · Cliente · web móvil](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369a66c5)
- [04 · Acceso y activación](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369ad12f)
- [05 · Administración · MVP](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369b7a3a)
- [06 · Pedidos y cocina · etapa 2](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369c6665)
- [07 · Crecimiento · futuro](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369cfc92)
- [08 · Plataforma y soporte](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369db5b4)
- [09 · Estados y accesibilidad](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369e3c33)
- [10 · resume.md](https://design.penpot.app/#/workspace/275e4692-9a43-8087-8008-ecfe91b8bf6f/a2455985-7d2b-80e1-8008-ed02369eac23)

## Herramientas y documentación

- [Penpot](https://penpot.app/): diseño y prototipado.
- [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/) y [Next.js](https://nextjs.org/docs): tecnologías propuestas, pendientes de decisión final.
- [Git](https://git-scm.com/doc): control de versiones.
- [Repositorio en GitHub](https://github.com/Sebastian-Fals/Sistema-restaurantes).

El diseño se elaboró aplicando las skills Impeccable y Design Taste Frontend disponibles en el entorno de trabajo.

## Organización prevista del repositorio

- Remoto SSH: `git@github.com:Sebastian-Fals/Sistema-restaurantes.git`.
- Rama inicial solicitada: `master`.
- Rama de desarrollo solicitada: `development`.
- Ambas deben partir del mismo commit inicial con este archivo.

