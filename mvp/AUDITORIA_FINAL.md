# Auditoría independiente de cambios del MVP

Fecha: 11 de noviembre de 2026. Rama local: `feat/mvp-pilot-readiness`.

## Resultado

La revisión independiente encontró un fallo de redirección posterior al acceso. Se comunicó al agente principal, se reasignó la corrección a un subagente y se volvió a revisar la solución. El fallo está corregido y sus pruebas de regresión pasan.

No quedan otros hallazgos accionables de corrección o seguridad identificados en el código revisado. Esto no equivale a una certificación de seguridad ni acredita una instalación productiva todavía no configurada.

## Cobertura

Se inspeccionaron tanto los cambios de archivos versionados frente a `HEAD` como los nuevos archivos sin versionar. La revisión comprendió:

- Dominio, puertos, casos de uso y adaptador de fidelización: contribuciones exactas de sellos, reversos, referencias idempotentes y orden de bloqueos.
- Modelo `StampContribution`, migración `0002_stamp_contributions`, reconstrucción de historiales y comportamiento conservador frente a procedencia ambigua.
- Identidad: desafíos de acceso, código de última emisión, alta concurrente, limpieza de datos personales, revocación de sesiones y comandos de retención/configuración de correo.
- Interfaz: resumen con periodo seleccionable, métricas, permisos, recuperación de errores, respuestas inciertas de compras/canjes/reversos, formularios y navegación posterior al acceso.
- Contacto de soporte configurable y propagación de la variable pública durante la compilación Docker.
- Pruebas nuevas de regresión y concurrencia, servidor aislado de aceptación, configuración y ejecutor de Playwright, dependencias y jobs de CI.
- Documentación operativa y diferencias intencionales entre los boards de Penpot y el alcance funcional del piloto.

Los criterios visuales de landing pages que exigen heroes de pantalla completa, efectos o nuevos bloques comerciales no se consideran defectos del producto: esta interfaz sirve para operar un programa de fidelización y sigue el diseño y el alcance explícitos. La auditoría no declara aprobado el checker genérico de landing pages.

## Hallazgo y corrección comprobada

### P1 — Redirección externa mediante caracteres de control: corregido

**Ubicación original:** `apps/web/src/app/acceso/page.tsx`, guardia de destino posterior al acceso, alrededor de la línea 78.

**Desencadenante:** `?next=%2F%09%2Fattacker.example`, y variantes con salto de línea o retorno de carro. La guardia basada en `startsWith("/")`, rechazo de `"//"` y barras invertidas aceptaba el valor decodificado `/\t/attacker.example`. La normalización WHATWG de URL elimina ese tabulador y produce un destino de otro origen. Un enlace de acceso manipulado podía enviar al usuario a un sitio externo después de autenticarse.

**Reproducción independiente previa:** Node evaluó la guardia como verdadera para las variantes TAB/LF/CR y `new URL(value, "http://127.0.0.1:3000").href` resolvió a `http://attacker.example/`.

**Corrección revisada:** `apps/web/src/features/auth/safe-redirect.ts` valida el valor contra el origen real, rechaza controles y barras invertidas en representaciones crudas y codificadas, comprueba el origen tras normalizar y rechaza resultados relativos a protocolo. El llamador utiliza `window.location.origin` y una ruta interna segura como alternativa.

**Pruebas independientes posteriores:** `pnpm test:security` obtuvo **6 passed**, incluyendo destinos locales válidos, URLs externas/esquemas/barras, controles crudos y codificados, el parámetro `next` decodificado, escapes malformados y exceso de capas de codificación. Se revisó también la integración de ese comando en el job web de CI.

## Verificación

- Ejecución independiente de `apps/api/.venv/bin/python -m pytest -q`: **58 passed, 5 skipped**. Las cinco omisiones son pruebas de bloqueos que requieren PostgreSQL y no se interpretan como aprobadas por SQLite.
- Ejecución independiente de `pnpm test:security`: **6 passed** tras la corrección del hallazgo.
- El agente principal aportó ejecución de **63 pruebas aprobadas en PostgreSQL 17**, incluidas las cinco de concurrencia, y **3 pruebas de aceptación Chrome aprobadas** que recorren los seis flujos, respuestas de compra/canje perdidas, teclado y adaptación a 320 px.
- Después de integrar la corrección del hallazgo, el agente principal repitió la aceptación (**3 passed**), seguridad (**6 passed**), TypeScript y la compilación de producción, todas correctas. Confirmó además `git diff --check` limpio y tipos generados OpenAPI sin cambios. El backend no cambió desde la pasada de 63 pruebas en PostgreSQL.

No se modificó código de producto desde este subagente auditor. La corrección del hallazgo se ejecutó por otro subagente, conforme a la instrucción del usuario.

## Límites que siguen siendo de despliegue y operación

- Configurar la dirección pública donde clientes y personal usarán la aplicación, HTTPS y PostgreSQL del piloto. Las ventas presenciales no exigen cobros integrados ni una tienda en línea.
- Definir un contacto real de soporte. Sin configuración, la interfaz dirige al equipo que activó el programa y no publica una dirección ficticia.
- Configurar el remitente y las credenciales de correo en el entorno y comprobar un envío real autorizado. El comando de configuración no prueba DNS ni entrega del proveedor, y esta auditoría no envió correos reales.
- Programar limpieza de códigos y sesiones, comprobar respaldo/recuperación y acordar incorporación y seguimiento del negocio piloto según `operacion.md`.
- Aplicar la migración y revisar con soporte historiales anteriores no reconstruibles. El código no inventa la procedencia de sellos ni corrige automáticamente esos saldos.
- La comprobación con navegadores automatizados no reemplaza la aceptación con dispositivos físicos o lectores de pantalla.

No se hizo push ni se modificó la rama durante la auditoría.
