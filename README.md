# Mesa — piloto de programa de sellos

Alcance: `mvp/alcance.md`. Stack: `stack.md`. Monolito modular: Django/DRF (`apps/api`) + Next.js (`apps/web`).

## Arquitectura (apps/api/mesa)
Hexagonal por módulo (`identity`, `loyalty`): `domain.py` (reglas puras) → `ports.py` (Protocols) →
`use_cases.py` (comandos) → `adapters/` (ORM, Resend/consola) → `api/` (DRF). `container.py` es la raíz de composición.
Las lecturas van por `selectors.py` (CQRS ligero). Idempotencia: `reference` única por negocio.

## Desarrollo
Requisitos: Python 3.12 + [uv](https://docs.astral.sh/uv/), Node 22 + pnpm (versión fijada en `packageManager`).
```bash
cd apps/api && uv sync
DEBUG=true uv run python manage.py migrate
DEBUG=true uv run python manage.py seed_demo              # negocio demo /b/cafe-olivo
DEBUG=true uv run python manage.py runserver              # :8000 (SQLite local si no hay DATABASE_URL)
cd ../web && pnpm install && pnpm dev                     # :3000, proxy /api -> localhost:8000
```
Los códigos de acceso salen por el log si no hay `RESEND_API_KEY`.

## Tests
```bash
cd apps/api && uv run pytest                                                  # SQLite en memoria
DATABASE_URL=postgres://usuario:clave@localhost:5432/mesa uv run pytest       # contra PostgreSQL, como en CI
cd ../web && pnpm typecheck && pnpm build
```

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
