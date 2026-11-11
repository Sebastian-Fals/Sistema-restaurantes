# Graph Report - sistema_restaurantes  (2026-11-11)

## Corpus Check
- Corpus is ~22,346 words - fits in a single context window. You may not need a graph.

## Summary
- 766 nodes · 1767 edges · 35 communities (20 shown, 15 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 95 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Interfaz y navegación web
- Reglas del dominio
- API de fidelización
- Persistencia y consultas
- Identidad y correo
- Alcance y decisiones arquitectónicas
- Composición y casos de uso
- Contrato OpenAPI y tipos
- Integración continua
- Pruebas de fidelización
- Autenticación y sesiones
- Serialización de respuestas
- Despliegue y proxy
- Puertos de identidad
- Configuración de TypeScript
- Configuración y arranque Django
- Administración interna
- Dependencias del backend
- Registro de aplicaciones Django
- Diseño global y layout
- Tipos generados por Next

## God Nodes (most connected - your core abstractions)
1. `DjangoLoyaltyRepository` - 37 edges
2. `LoyaltyRepository` - 28 edges
3. `errorMessage()` - 20 edges
4. `DomainError` - 19 edges
5. `User` - 19 edges
6. `next` - 18 edges
7. `Alcance del prototipo vendible` - 17 edges
8. `Decisiones y evolución del stack` - 17 edges
9. `buy()` - 16 edges
10. `compilerOptions` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Correo por Resend o consola` --references--> `make_mailer()`  [EXTRACTED]
  README.md → apps/api/mesa/identity/adapters/mailers.py
- `Reversos auditables con actor y motivo` --conceptually_related_to--> `NeedsSupport`  [INFERRED]
  mvp/alcance.md → apps/api/mesa/loyalty/domain.py
- `Un sello por compra pagada elegible` --conceptually_related_to--> `is_eligible()`  [INFERRED]
  mvp/alcance.md → apps/api/mesa/loyalty/domain.py
- `Un sello por compra pagada elegible` --conceptually_related_to--> `add_stamp()`  [INFERRED]
  mvp/alcance.md → apps/api/mesa/loyalty/domain.py
- `Configuración asistida: negocio, sede, menú y programa` --conceptually_related_to--> `Business`  [INFERRED]
  mvp/alcance.md → apps/api/mesa/loyalty/models.py

## Import Cycles
- 1-file cycle: `apps/api/config/settings.py -> apps/api/config/settings.py`
- 1-file cycle: `apps/api/config/urls.py -> apps/api/config/urls.py`
- 1-file cycle: `apps/api/config/wsgi.py -> apps/api/config/wsgi.py`
- 1-file cycle: `apps/api/manage.py -> apps/api/manage.py`
- 1-file cycle: `apps/api/mesa/identity/api.py -> apps/api/mesa/identity/api.py`
- 1-file cycle: `apps/api/mesa/loyalty/api/views.py -> apps/api/mesa/loyalty/api/views.py`
- 1-file cycle: `apps/api/mesa/container.py -> apps/api/mesa/container.py`
- 1-file cycle: `apps/api/mesa/identity/adapters/orm.py -> apps/api/mesa/identity/adapters/orm.py`
- 1-file cycle: `apps/api/mesa/identity/use_cases.py -> apps/api/mesa/identity/use_cases.py`
- 1-file cycle: `apps/api/mesa/identity/domain.py -> apps/api/mesa/identity/domain.py`
- 1-file cycle: `apps/api/tests/conftest.py -> apps/api/tests/conftest.py`
- 1-file cycle: `apps/api/mesa/identity/models.py -> apps/api/mesa/identity/models.py`
- 1-file cycle: `apps/api/mesa/identity/apps.py -> apps/api/mesa/identity/apps.py`
- 1-file cycle: `apps/api/mesa/identity/ports.py -> apps/api/mesa/identity/ports.py`
- 1-file cycle: `apps/api/mesa/loyalty/management/commands/seed_demo.py -> apps/api/mesa/loyalty/management/commands/seed_demo.py`
- 1-file cycle: `apps/api/mesa/loyalty/selectors.py -> apps/api/mesa/loyalty/selectors.py`
- 1-file cycle: `apps/api/mesa/loyalty/api/permissions.py -> apps/api/mesa/loyalty/api/permissions.py`
- 1-file cycle: `apps/api/mesa/loyalty/ports.py -> apps/api/mesa/loyalty/ports.py`
- 1-file cycle: `apps/web/next-env.d.ts -> apps/web/next-env.d.ts`
- 2-file cycle: `apps/api/mesa/container.py -> apps/api/mesa/identity/adapters/mailers.py -> apps/api/mesa/container.py`

## Hyperedges (group relationships)
- **Flujo completo de fidelización del piloto** — mvp_alcance_identidad, mvp_alcance_sellos, mvp_alcance_canje, mvp_alcance_reversos, mvp_alcance_permisos, mvp_alcance_idempotencia [EXTRACTED 1.00]

## Communities (35 total, 15 thin omitted)

### Community 0 - "Interfaz y navegación web"
Cohesion: 0.06
Nodes (75): /api/v1/auth/logout, /api/v1/b/{slug}/activity, /api/v1/me, /api/v1/public/b/{slug}, api, csrf, errorMessage(), Schemas (+67 more)

### Community 1 - "Reglas del dominio"
Cohesion: 0.06
Nodes (29): DomainError, hash_code(), InvalidCode, normalize_email(), TooManyRequests, add_stamp(), AlreadyReversed, CardState (+21 more)

### Community 2 - "API de fidelización"
Cohesion: 0.07
Nodes (36): activate_card(), BusinessScoped, _HasRole, IsBusinessAdmin, IsBusinessStaff, CardSerializer, /api/v1/b/{slug}/card, /api/v1/b/{slug}/consent (+28 more)

### Community 3 - "Persistencia y consultas"
Cohesion: 0.08
Nodes (26): DjangoLoyaltyRepository, _purchase(), _reward(), Business, Card, Meta, Consent, Meta (+18 more)

### Community 4 - "Identidad y correo"
Cohesion: 0.07
Nodes (29): verify_login_code(), ConsoleMailer, make_mailer(), ResendMailer, DjangoLoginCodeStore, DjangoUserDirectory, PendingCode, Migration (+21 more)

### Community 5 - "Alcance y decisiones arquitectónicas"
Cohesion: 0.07
Nodes (20): Alcance del prototipo vendible, Alta manual desde Django admin, Instrucciones del negocio piloto, Compra, canje y reversos sin duplicados, Cliente: /b/<slug>, código de 6 dígitos válido 10 minutos, Administrador y atención en /app/<slug>, Incorporación, soporte y revisión por piloto, CI: pytest, tipos, build y Docker (+12 more)

### Community 6 - "Composición y casos de uso"
Cohesion: 0.10
Nodes (22): delete_account(), lookup_customer(), redeem_reward(), register_purchase(), reverse_purchase(), set_consent(), ActivateCard, DeleteAccount (+14 more)

### Community 7 - "Contrato OpenAPI y tipos"
Cohesion: 0.08
Nodes (34): dependencies, next@^16.4.6, openapi-fetch@^0.17.0, react@^19.3.1, react-dom@^19.3.1, devDependencies, openapi-typescript@^7.13.0, @types/node@^26.6.6 (+26 more)

### Community 8 - "Integración continua"
Cohesion: 0.11
Nodes (37): defaults, env, runs-on, services, steps, run, runs-on, steps (+29 more)

### Community 9 - "Pruebas de fidelización"
Cohesion: 0.12
Nodes (29): admin(), buy(), clean_outbox(), client_for(), customer(), make_business(), make_user(), olivo() (+21 more)

### Community 10 - "Autenticación y sesiones"
Cohesion: 0.11
Nodes (17): request_login_code(), CsrfView, EmailSerializer, /api/v1/auth/code, /api/v1/auth/csrf, /api/v1/auth/verify, LogoutView, RequestCodeView (+9 more)

### Community 11 - "Serialización de respuestas"
Cohesion: 0.09
Nodes (23): ActivitySerializer, ConsentSerializer, CustomerLookupSerializer, DailyStampsSerializer, DateRangeSerializer, ErrorSerializer, MembershipSerializer, MenuItemSerializer (+15 more)

### Community 12 - "Despliegue y proxy"
Cohesion: 0.14
Nodes (25): config, build, condition, env_file, extra_hosts, healthcheck, ports, restart (+17 more)

### Community 13 - "Puertos de identidad"
Cohesion: 0.16
Nodes (9): LoginCodeStore, Mailer, UserDirectory, RequestLoginCode, VerifyLoginCode, collections_abc, django_utils, secrets (+1 more)

### Community 14 - "Configuración de TypeScript"
Cohesion: 0.19
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 15 - "Configuración y arranque Django"
Cohesion: 0.17
Nodes (8): test_committed_openapi_is_up_to_date(), dj_database_url, django_core_management, django_core_wsgi, os, pathlib, sys, yaml

### Community 16 - "Administración interna"
Cohesion: 0.23
Nodes (5): BusinessAdmin, MembershipInline, MenuInline, ProgramInline, ReadOnly

### Community 17 - "Dependencias del backend"
Cohesion: 0.20
Nodes (9): pkg_dj_database_url, pkg_django, pkg_djangorestframework, pkg_drf_spectacular, pkg_gunicorn, mesa-api, pkg_psycopg, pkg_resend (+1 more)

### Community 18 - "Registro de aplicaciones Django"
Cohesion: 0.29
Nodes (3): IdentityConfig, LoyaltyConfig, django_apps

### Community 19 - "Diseño global y layout"
Cohesion: 0.33
Nodes (3): metadata, sans, serif

## Knowledge Gaps
- **31 isolated node(s):** `Square Loyalty`, `Loopy Loyalty`, `Toast KDS`, `Fivestars`, `Penpot Sistema de restaurantes` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 124 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Mesa: desarrollo y arquitectura actual` connect `Alcance y decisiones arquitectónicas` to `Composición y casos de uso`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DjangoLoyaltyRepository` (e.g. with `User` and `Card`) actually correct?**
  _`DjangoLoyaltyRepository` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Square Loyalty`, `Loopy Loyalty`, `Toast KDS` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Interfaz y navegación web` be split into smaller, more focused modules?**
  _Cohesion score 0.06404040404040404 - nodes in this community are weakly interconnected._
- **Why does `CI: pytest, tipos, build y Docker` connect `Alcance y decisiones arquitectónicas` to `Integración continua`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `LoyaltyRepository` (e.g. with `CardState` and `ProgramState`) actually correct?**
  _`LoyaltyRepository` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Reglas del dominio` be split into smaller, more focused modules?**
  _Cohesion score 0.05664568678267309 - nodes in this community are weakly interconnected._
## Cobertura y límites de esta ejecución

Se incluyen los archivos detectados y nodos adicionales para Docker, CSS, archivos de configuración y dependencias. Las rutas HTTP conectan frontend y vistas Django mediante coincidencias explícitas. Los documentos históricos pueden describir planes futuros; sus relaciones no prueban implementación.

El JSON conserva las relaciones paralelas originales; el análisis de comunidades y la visualización pueden agruparlas. Las conexiones dinámicas no son exhaustivas.

Tokens semánticos: no disponibles en la herramienta de subagentes de esta sesión; los ceros del contador automático son marcadores, no consumo real. No se usó una API Gemini externa.

`graphify-out/` se escribió en el árbol de trabajo y no está ignorado por Git. Se puede ignorar la carpeta o versionar los artefactos que el equipo quiera compartir.

Diagnóstico: 0 extremos ausentes, 0 referencias rotas y 0 autorrelaciones. El análisis como grafo simple agrupa 100 relaciones paralelas; graph.json conserva las 1.867 relaciones originales. Véase HEALTH_REPORT.txt.
