# Operación del piloto Mesa

Esta guía cierra la preparación técnica y operativa de `alcance.md`. El servicio es un piloto de fidelización: no cobra, no factura y no reemplaza la caja del negocio.

## Preparación por negocio

El equipo Mesa acuerda con el negocio el periodo del piloto, un responsable, un canal de soporte comprobado y la fecha de revisión. El correo de soporte mostrado en la interfaz debe ser un buzón atendido antes de compartir la aplicación con clientes.

El frontend lee `NEXT_PUBLIC_SUPPORT_EMAIL` al compilar. En desarrollo se configura en `apps/web/.env.local`
(ver `.env.example`); en Docker se exporta la variable antes de `docker compose build`, o se define en el
archivo `.env` de Compose en la raíz. Después de cambiar el canal debe recompilarse el frontend. Si no
hay una dirección válida, la interfaz indica que se contacte al equipo que activó el negocio y no publica
un correo ficticio. Esta variable es pública y no debe contener credenciales.

Desde el admin interno se configuran nombre, dirección de la única sede, contactos, menú y disponibilidad, programa de sellos y membresías de administrador y atención. La compra mínima, sellos, recompensa, vigencia y condiciones se acuerdan por piloto; los valores de Café Olivo son sintéticos.

Se entrega la URL o QR de `/b/<slug>` y las instrucciones de `piloto.md`. Un QR público solo identifica el negocio. El personal sigue verificando el pago en su caja existente.

## Correo real de acceso

1. Configurar en Resend el dominio remitente y completar su verificación. El equipo necesita una API key autorizada para enviar desde ese dominio; no se guarda en Git.
2. Configurar en `apps/api/.env` o en el gestor de secretos `RESEND_API_KEY`, `RESEND_FROM` y `MAIL_ADAPTER=resend`. `RESEND_FROM` acepta el formato `Mesa <acceso@dominio-del-negocio>` con una dirección real del dominio verificado.
3. Ejecutar desde `apps/api`:

   ```bash
   uv run python manage.py check_mail_configuration
   ```

   En Docker: `docker compose exec -T api python manage.py check_mail_configuration`.

   El comando es de solo lectura: verifica adaptador, presencia de clave y formato del remitente, rechaza dominios de ejemplo y no imprime secretos ni envía correo. Un resultado correcto no verifica DNS, permisos de la API key ni entrega del proveedor.
4. Con una dirección y un envío autorizados, solicitar un código desde `/acceso`, comprobar recepción, entrar con el código y verificar que no se puede reutilizar. Revisar también el reenvío después de 60 segundos. Conservar solo el resultado de la comprobación, sin copiar códigos ni claves a reportes o tickets.

La demo local usa `MAIL_ADAPTER=console`: muestra los códigos en el log de desarrollo y no acredita que funcione la entrega real. El piloto real no debe usar ese adaptador.

## Datos de cuenta y retención de accesos

La eliminación desactiva la cuenta y anonimiza su correo. Conserva compras, tarjetas, recompensas y reversos con sus relaciones para mantener el historial operativo; borra consentimientos, desafíos de acceso del correo original y sesiones de la cuenta. Registrarse otra vez con ese mismo correo crea otra cuenta que no hereda las tarjetas anteriores.

Los códigos duran 10 minutos. Solo la última emisión puede verificarse; al emitir otra se invalidan las anteriores. Los códigos consumidos permanecen hasta vencer para conservar el periodo de espera y evitar que un código antiguo vuelva a ser aceptado. Después del vencimiento se eliminan con:

```bash
docker compose exec -T api python manage.py purge_login_codes
```

El operador programa ese comando cada 15 minutos con su planificador. La retención normal de estos registros queda limitada al tiempo de vigencia más el intervalo de limpieza, mientras el planificador funcione. El comando informa únicamente la cantidad eliminada y conserva los desafíos todavía vigentes, incluidos los consumidos recientemente.

Ejecutar también `docker compose exec -T api python manage.py clearsessions` diariamente para borrar sesiones vencidas. Los logs de consola son exclusivos de desarrollo. La retención de logs operativos, respaldos y tickets se define en el entorno de despliegue y debe respetar la minimización acordada para el piloto; borrar una cuenta no reescribe respaldos históricos.

## Despliegue y prueba de aceptación

- Usar PostgreSQL externo con credenciales propias del entorno, migraciones aplicadas y un respaldo recuperable. Probar recuperación antes de depender de la aplicación durante el servicio.
- Mantener `DEBUG=false`, `SECRET_KEY` aleatoria, `ALLOWED_HOSTS` acotados, origen público HTTPS en `CSRF_TRUSTED_ORIGINS` y `COOKIE_SECURE=true`. El frontend y la API usan el mismo origen público mediante el proxy de Next.
- Ejecutar `python manage.py check --deploy` con los valores reales, revisar cada aviso y comprobar TLS en el proxy de despliegue. La configuración de TLS, dominio y servidor no está aprovisionada por ejecutar las pruebas locales.
- Recorrer descubrimiento, alta, tarjeta vacía, compra, reintento sin duplicado, recompensa, canje, rechazo de segundo canje y reverso. Repetir con usuario de otro negocio y con atención intentando tareas de administrador.
- Validar móvil a 320 px, teclado, carga, errores recuperables y desconexión durante una compra o un canje. Ante una respuesta de red incierta, comprobar el estado existente antes de registrar una nueva operación.
- Ejecutar las pruebas de concurrencia con PostgreSQL; SQLite local no demuestra el comportamiento de los bloqueos de producción.

## Seguimiento sin ampliar el producto

El resumen y la actividad aportan compras, sellos, clientes que regresan y recompensas. Durante el piloto, el equipo lleva una hoja de seguimiento con visitas y altas observadas, duplicados/rechazos reportados, primera operación del personal, tiempo de soporte, incidentes y reclamos. No anotar códigos de acceso ni datos de pago.

La revisión con cada negocio compara esas observaciones con sus objetivos y define continuidad. No se atribuye causalidad ni se promete un aumento de ventas. Campañas, pagos, pedidos, varias sedes y analítica avanzada continúan fuera de alcance.
