# Mesa — piloto de programa de sellos

Alcance: `mvp/alcance.md`. Stack: `stack.md`. Monolito modular: Django/DRF (`apps/api`) + Next.js (`apps/web`).

## Arquitectura (apps/api/mesa)
Hexagonal por módulo (`identity`, `loyalty`): `domain.py` (reglas puras) → `ports.py` (Protocols) →
`use_cases.py` (comandos) → `adapters/` (ORM, Resend/consola) → `api/` (DRF). `container.py` es la raíz de composición.
Las lecturas van por `selectors.py` (CQRS ligero). Idempotencia: `reference` única por negocio.

Patrones: **Ports & Adapters** (los casos de uso solo conocen `Protocol`s; Django vive en `adapters/` y `api/`) ·
**Repository** (`DjangoLoyaltyRepository`, `DjangoLoginCodeStore`) · **Command/Use Case** (`RegisterPurchase`,
`ActivateCard`, `LookupCustomer`, `DeleteAccount`…: un objeto invocable por intención) · **Composition Root**
(`container.py`, único sitio que instancia adaptadores) · **Strategy** (`make_mailer`: Resend o consola según
configuración) · **CQRS ligero** (comandos por casos de uso, lecturas por `selectors.py`). Las vistas solo validan,
llaman a `container.*()`/selectors y serializan; los casos de uso se prueban con dobles sin BD (`tests/test_use_cases.py`).

## Desarrollo
Requisitos: Python 3.12 + [uv](https://docs.astral.sh/uv/), Node 22 + pnpm (versión fijada en `packageManager`).
```bash
cd apps/api && uv sync
# DATABASE_URL es obligatoria (PostgreSQL externo). Definela en apps/api/.env o en el entorno.
DEBUG=true uv run python manage.py migrate
DEBUG=true uv run python manage.py seed_demo              # negocio demo /b/cafe-olivo
DEBUG=true uv run python manage.py runserver              # :8000
cd ../web && pnpm install && pnpm dev                     # :3000, proxy /api -> localhost:8000
```
Los códigos de acceso salen por el log si no hay `RESEND_API_KEY`.

## Tests
```bash
cd apps/api && uv run pytest                                                  # SQLite en memoria (solo tests)
DATABASE_URL=postgres://usuario:clave@localhost:5432/mesa uv run pytest       # contra PostgreSQL, como en CI
cd ../web && pnpm typecheck && pnpm test:security && pnpm build
```

Aceptación en navegador (requiere las dependencias de API instaladas y Chrome, o Chromium de Playwright):

```bash
cd apps/web
pnpm test:e2e
# Alternativa sin Chrome del sistema:
pnpm exec playwright install chromium
PLAYWRIGHT_CHROMIUM_CHANNEL=chromium pnpm test:e2e
```

Estas pruebas levantan una API con datos sintéticos y base temporal en `:8011` y un frontend en `:3011`;
no reutilizan la base de la demo ni una base productiva. Comprueban los seis recorridos, teclado,
anchos de 320–1440 px y respuestas de compra/canje perdidas. Se conserva la configuración TypeScript
original al terminar. El job `acceptance` ejecuta el mismo recorrido en CI.

Preparación de un piloto real y retención de accesos: [`mvp/operacion.md`](mvp/operacion.md).
La migración `0002_stamp_contributions` registra qué compras contribuyeron a cada recompensa.
Los historiales anteriores con reversos o saldos no reconstruibles se escalan a soporte; no se inventa
su procedencia. Antes de desplegar, aplicar migraciones y revisar esos casos con el equipo.

## Contrato OpenAPI → tipos del frontend
```bash
cd apps/api && uv run python manage.py spectacular --file openapi.yaml   # drf-spectacular
cd ../web && pnpm gen:api                                               # openapi-typescript → src/api/schema.d.ts
```
Un test falla si `openapi.yaml` no está al día, y CI falla si `schema.d.ts` no coincide con `pnpm gen:api`.

## Despliegue (docker compose, BD externa)
El compose levanta solo `api` (Django + gunicorn) y `web` (Next standalone); PostgreSQL es **externo**.
```bash
cp apps/api/.env.example apps/api/.env      # define DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, RESEND_*, COOKIE_SECURE
docker compose up -d --build                # la api aplica migraciones al arrancar
docker compose exec api python manage.py createsuperuser
```
Web en `:3000`; el admin interno de Django queda en `127.0.0.1:8000/admin` (solo desde la máquina). Ahí el superusuario
da de alta el negocio, su programa, menú y personal (Membership admin/staff). Datos demo opcionales:
`docker compose exec api python manage.py seed_demo`. Si la BD corre en el mismo host que Docker, usa
`host.docker.internal` como host en `DATABASE_URL`.

## CI
`.github/workflows/ci.yml` (push y pull_request): `api` (uv + pytest contra un servicio PostgreSQL 17), `web`
(typecheck, build y tipos OpenAPI al día) y `docker` (`docker compose build`).
