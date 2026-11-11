# Instrucciones para el negocio piloto — Mesa

Documento para el equipo del negocio piloto. Complementa `mvp/alcance.md` (alcance del prototipo) y `README.md` (desarrollo).

## 1. Qué es Mesa

Programa digital de sellos para cafeterías. El cliente acumula un sello por compra pagada y elegible; al completar el objetivo recibe una recompensa. **Mesa no cobra, no factura y no reemplaza el POS ni los registros obligatorios del negocio.** El pago se sigue haciendo en la caja actual.

## 2. Cómo se configura el negocio (equipo Mesa)

La configuración inicial la realiza el equipo de Mesa desde el admin interno de Django (`http://127.0.0.1:8000/admin` en el piloto, o el host acordado). Se configura una vez por negocio:

- Nombre visible, slug/URL, descripción, dirección y datos de contacto.
- Menú público: productos con categoría, descripción, precio informativo y disponibilidad.
- Un programa de sellos activo: recompensa, sellos requeridos, compra mínima, vigencia de la recompensa y condiciones.
- Cuentas de personal con rol **administrador** o **atención** (acceso por correo + código de un solo uso).

Los valores del diseño de Penpot son ejemplos; los valores reales se acuerdan por piloto.

## 3. Cómo usa el personal

URL del panel: `https://<host>/app/<slug>` (el slug se entrega en la incorporación).

- **Atención (barista):** busca al cliente por correo o código (ej. `CAF · 482 916`), registra la compra con comprobante y monto, confirma el canje de una recompensa disponible.
- **Administrador:** además ve el resumen, la actividad con filtros por fecha y tipo, el detalle de cada operación y puede anular una compra con motivo.

El personal confirma en la app que el cobro ocurrió en caja; Mesa no verifica el pago.

## 4. Cómo se registra un cliente

1. El cliente abre la página pública del negocio (`/b/<slug>`) desde el QR o el enlace.
2. Revisa el menú y las reglas del programa.
3. Se registra con su correo; recibe un código de 6 dígitos válido 10 minutos.
4. Activa su tarjeta (vacía) y ve su progreso, sellos y recompensas.

## 5. Límites del servicio (fuera de alcance del piloto)

No se incluyen en este prototipo:

- Cobro con tarjeta, transferencias, billeteras o pagos integrados.
- Caja registradora, arqueo, conciliación financiera o sustitución del POS.
- Facturación electrónica o integración con la DIAN.
- Mesas, pedidos en línea, comandas, cocina/barra.
- Inventario, costos, contabilidad, nómina.
- Varias sedes por negocio, franquicias, roles complejos.
- Campañas, notificaciones promocionales, segmentación.
- Apple Wallet/Google Wallet, apps nativas.
- Analítica avanzada, tableros configurables.
- Autoservicio para alta de negocios o configuración del programa.

Si el negocio requiere alguna de estas funciones, se registra como necesidad de producto y se acuerda por separado.

## 6. Reglas operativas

- Una compra elegible genera como máximo un sello.
- Toda compra y canje tiene referencia única; repetir la misma operación no duplica.
- Las correcciones se registran como reversos con motivo, actor y fecha; no se borra el historial. Si la recompensa derivada ya fue canjeada, el caso se escala a soporte.
- El cliente no puede acreditar su propio sello con el QR público.
- El personal solo opera en el negocio para el que tiene permiso.
- El consentimiento comercial es opcional, por negocio y canal, y revocable desde "Mi cuenta".
- Los cierres, reportes y métricas del prototipo no constituyen libros contables ni reportes fiscales.

## 7. Soporte

- Canal de reporte de problemas: **soporte@mesa.app** (ajustar al canal acordado en la incorporación).
- Periodo de piloto, canal de revisión y criterio de continuación se definen con cada negocio antes de activarlo.
- El producto se ofrece como piloto de software en desarrollo, con funciones y disponibilidad limitadas.

## 8. Requisitos técnicos mínimos

- Navegador actualizado en móvil o escritorio (Chrome, Safari, Edge, Firefox).
- Conexión a internet para el personal y los clientes.
- El panel se usa durante el servicio; se recomienda pantalla de al menos 320 px de ancho.