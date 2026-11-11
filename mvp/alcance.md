# Alcance del prototipo vendible

**Nombre de trabajo:** Mesa  
**Versión:** 0.1  
**Estado:** propuesta de alcance para un piloto comercial  
**Contexto:** cafeterías independientes en Colombia; interfaz en español y valores en COP.

## 1. Propósito

Entregar una versión pequeña, funcional y demostrable que una cafetería pueda usar con clientes reales para probar un programa digital de sellos. El piloto debe ayudar a vender el servicio, observar si clientes y personal lo entienden y financiar la evolución del producto.

El éxito es validar el flujo de fidelización con uno o pocos negocios piloto, no reemplazar el POS ni completar desde el inicio una plataforma integral de operación de restaurantes.

## 2. Resultado que recibe el cliente piloto

- Un negocio y una sede configurados por el equipo de Mesa.
- Una página pública del negocio con menú informativo y programa de sellos.
- Una tarjeta digital accesible desde el teléfono del cliente.
- Una pantalla privada y sencilla para el personal: buscar al cliente, registrar una compra elegible y confirmar un canje.
- Un resumen básico de actividad para el dueño o administrador.
- Acompañamiento de incorporación y un canal para reportar problemas durante el piloto.

El servicio se ofrece como **piloto de software en desarrollo**, con funciones y disponibilidad limitadas. No prometer integración con cajas, bancos, billeteras, contabilidad o la DIAN.

## 3. Alcance funcional incluido

### 3.1 Configuración del negocio

El equipo Mesa configura manualmente:

- Nombre visible, slug/URL, descripción, dirección y datos de contacto.
- Una sede.
- Menú público básico: nombre, descripción y precio informativo por producto; categorías sencillas y disponibilidad visible.
- Un programa de sellos activo por negocio.
- Una recompensa, su cantidad de sellos y condiciones esenciales.
- Cuentas de personal con rol de administrador o personal de atención.

La configuración inicial puede realizarse con herramientas internas; no se construirá un asistente de autoservicio completo en esta fase.

### 3.2 Programa de fidelización

- El cliente consulta las reglas antes de registrarse.
- El programa indica compra mínima, cantidad de sellos requeridos, recompensa y vigencia cuando aplique.
- Los valores son configurables por el equipo para cada piloto. Los valores y productos del prototipo de Penpot son ejemplos, no condiciones comerciales predefinidas.
- Una compra pagada y elegible acredita como máximo un sello.
- La tarjeta muestra progreso, sellos obtenidos y recompensa disponible.
- El código QR público identifica el negocio; no demuestra que una compra ocurrió.

### 3.3 Cliente

- Registro e inicio de sesión con correo electrónico y código de verificación de un solo uso.
- Recuperación mediante el mismo flujo de verificación.
- Consulta de tarjeta, saldo de sellos, recompensa y actividad reciente.
- Consulta del menú y reglas del programa sin iniciar sesión.
- Preferencia de comunicaciones comerciales separada del acceso al servicio, opcional y revocable.
- Vista básica para revisar o solicitar eliminación de la cuenta, sujeta a los registros que deban conservarse.

Durante el piloto se puede limitar el alta a invitación o enlace/QR del negocio para controlar soporte y aprendizaje.

### 3.4 Registro de compra por el personal

- El personal autorizado busca al cliente por correo o identificador visible de su cuenta.
- Registra el valor de una compra que ya fue pagada en el punto de venta existente.
- La aplicación valida el mínimo elegible y acredita el sello correspondiente.
- Se registra quién hizo la operación, negocio/sede, fecha, valor y referencia interna única.
- Repetir una solicitud con la misma referencia no duplica compra ni sello; se devuelve el resultado existente.
- El cliente ve la actividad reflejada en su tarjeta.

La comprobación de pago se realiza en el proceso operativo del negocio. El personal confirma que el cobro ocurrió en su caja actual; el prototipo no cobra ni verifica directamente con el POS o una entidad financiera.

### 3.5 Canje

- El cliente presenta una recompensa disponible.
- El personal comprueba la recompensa en su sesión, confirma el canje y la marca como consumida.
- La confirmación no puede consumir dos veces la misma recompensa.
- Se guarda actor, hora y negocio/sede.
- La recompensa vencida, ya usada o no disponible no puede canjearse.

Para que el piloto sea rápido, el primer flujo puede ser una confirmación asistida en pantalla; el código temporal y su validación avanzada se dejan fuera salvo que el diseño/piloto confirme que son necesarios para evitar fraude operativo.

### 3.6 Panel del negocio

Panel mínimo con:

- Clientes registrados.
- Compras registradas y sellos acreditados en un periodo seleccionable sencillo.
- Recompensas disponibles y canjeadas.
- Lista de actividad reciente con filtros básicos por fecha y tipo.
- Detalle de operación para investigar un reclamo.

Las métricas describen actividad observada; no atribuyen causalidad ni prometen aumento de ventas o recurrencia.

## 4. Flujos que deben funcionar de principio a fin

1. **Descubrir:** cliente abre la página pública del negocio, revisa el menú y entiende el programa.
2. **Activar tarjeta:** cliente se registra con código de correo y ve su tarjeta vacía.
3. **Comprar y acreditar:** paga usando el proceso existente del local; el personal registra la compra una sola vez; el cliente ve el sello.
4. **Completar y canjear:** al alcanzar el objetivo, la recompensa aparece; personal la valida y la consume una sola vez.
5. **Administrar:** dueño consulta actividad básica y puede identificar quién registró una operación.
6. **Corregir un error:** administrador anula una compra mediante reverso registrado con motivo, sin borrar el evento original; si la recompensa derivada ya fue usada, se escala a soporte.

## 5. Fuera de alcance

No construir para este prototipo:

- Cobro con tarjeta, transferencias, billeteras, pagos integrados, custodia o liquidación de fondos.
- Caja registradora, apertura/cierre de caja, arqueo, conciliación financiera o sustitución del POS.
- Facturación electrónica, documentos equivalentes, integración directa DIAN o generación de documentos tributarios.
- Mesas, pedidos en línea, pedidos desde QR, comandas, cocina/barra o seguimiento de preparación.
- Inventario, costos, contabilidad, nómina o compras a proveedores.
- Varias sedes por negocio, franquicias, roles complejos o permisos configurables.
- Campañas, notificaciones promocionales automatizadas, segmentación o integraciones de marketing.
- Apple Wallet/Google Wallet, aplicaciones nativas, geolocalización o proximidad.
- División de cuentas, pagos parciales, propinas o reembolsos integrados.
- Analítica avanzada, predicción, atribución de campañas o tableros configurables.
- Autoservicio completo para alta de negocios, configuración del programa o publicación del menú.
- Personalización visual ilimitada, dominios propios o marca blanca.

Si un cliente requiere cualquiera de estas funciones para operar, se registra como necesidad de producto y se acuerda por separado; no se amplía el piloto sin revisar su impacto en fecha, soporte y riesgo.

## 6. Reglas y límites operativos

- Una compra elegible genera como máximo un sello; las reglas se muestran antes de la participación.
- Toda compra y canje tiene referencia única e idempotencia.
- Las correcciones se registran como reversos con motivo, actor y fecha; no se elimina el historial.
- El cliente no puede acreditar su propio sello mediante el QR público.
- El personal solo opera en el negocio/sede para el que tiene permiso.
- El sistema guarda únicamente los datos personales necesarios para cuenta, operación y soporte.
- Consentimiento comercial opcional, separado por negocio y canal; debe poder revocarse.
- Los cierres, reportes y métricas del prototipo no constituyen libros contables ni reportes fiscales.
- Se informa a cada negocio que el producto es un piloto y que no reemplaza sus registros obligatorios ni sus sistemas de cobro.

## 7. Criterios de aceptación

El prototipo se considera listo para ofrecerse a un piloto cuando:

- Un negocio puede ser configurado y su página pública abre desde móvil y escritorio.
- Un cliente puede consultar reglas, registrarse, iniciar sesión y ver su tarjeta.
- Un empleado autorizado puede registrar una compra pagada externamente y el sello aparece una sola vez.
- Repetir la misma operación no duplica compra ni sello.
- El personal puede validar y consumir una recompensa disponible una sola vez.
- Un administrador puede revisar actividad y registrar un reverso con motivo.
- La separación entre negocios impide que una cuenta de otro negocio vea o modifique datos ajenos.
- Los estados de carga, error, vacío, confirmación y éxito son comprensibles; la interfaz funciona a 320 px como mínimo y se puede operar con teclado.
- El negocio piloto recibe instrucciones de uso, límites del servicio y contacto de soporte.

## 8. Experiencia visual

Usar el archivo de Penpot y `resume.md` como referencia: superficies claras, verde bosque para acciones principales, Instrument Serif en titulares de marca y DM Sans para interfaz/datos. Mantener el flujo de cliente mobile-first y el panel de operación legible durante el servicio.

No implementar todas las pantallas que aparecen en Penpot. Para este alcance bastan las vistas públicas, acceso, tarjeta/actividad, registro de compra, confirmación de canje y resumen del negocio. Las rutas de pedidos/cocina, campañas, varias sedes y plataforma avanzada no forman parte del piloto.

## 9. Supuestos para mantener el plazo corto

- Un único tipo de negocio inicial: cafetería.
- Uno o pocos negocios piloto incorporados manualmente.
- Una sede y un programa por negocio.
- Un flujo de compra presencial con cobro realizado fuera del prototipo.
- Una recompensa principal, reglas simples y configuración asistida.
- Menú informativo, sin carrito ni promesa de disponibilidad en tiempo real.
- Volumen y soporte de piloto controlados; no se define aún un SLA de producción.

Si cualquiera de estos supuestos cambia, ajustar el alcance antes de iniciar implementación.

## 10. Indicadores del piloto

Medir para aprender, sin presentarlo como garantía comercial:

- Negocios incorporados y personal que completa su primera operación.
- Clientes que visitan la página y completan el registro.
- Compras elegibles registradas y tasa de duplicados/rechazos.
- Clientes que vuelven a realizar una compra observada en el periodo.
- Recompensas obtenidas y canjeadas.
- Tiempo y consultas de soporte por operación.
- Errores operativos o reclamos de clientes.

Definir con cada negocio periodo, canal de revisión y criterio de continuación del piloto antes de activarlo.

## 11. Guía para implementación futura y agentes de IA

- Este archivo limita el prototipo vendible; leer también `../resume.md` y `../stack.md`.
- No añadir funciones de la etapa 2 o futura salvo decisión explícita y revisión de alcance.
- Mantener el servidor como autoridad para permisos, reglas, idempotencia y aislamiento por negocio.
- Registrar operaciones de fidelización como eventos auditables; reversar en vez de borrar.
- No simular que un pago fue procesado, que una factura fue validada por DIAN o que una compra fue verificada por un proveedor externo.
- Priorizar el recorrido completo de fidelización sobre amplitud de pantallas, configuraciones o integraciones.
- Antes de empezar código, convertir este alcance en tareas pequeñas que se puedan demostrar dentro de esos seis flujos.
