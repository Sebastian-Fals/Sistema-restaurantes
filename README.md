# Mesa — piloto de programa de sellos

Alcance: `mvp/alcance.md`. Stack: `stack.md`. Monolito modular: Django/DRF (`apps/api`) + Next.js (`apps/web`).

## Arquitectura (apps/api/mesa)
Hexagonal por módulo (`identity`, `loyalty`): `domain.py` (reglas puras) → `ports.py` (Protocols) →
`use_cases.py` (comandos) → `adapters/` (ORM, Resend/consola) → `api/` (DRF). `container.py` es la raíz de composición.
Las lecturas van por `selectors.py` (CQRS ligero). Idempotencia: `reference` única por negocio.

## Desarrollo
```bash
cd apps/api && uv sync && uv run pytest                     # tests (SQLite en memoria)
DEBUG=true uv run python manage.py migrate && uv run python manage.py seed_demo && DEBUG=true uv run python manage.py runserver
cd apps/web && pnpm install && pnpm dev                     # proxy /api -> localhost:8000
```
Los códigos de acceso salen por el log si no hay `RESEND_API_KEY`.

## Contrato OpenAPI → tipos del frontend
```bash
cd apps/api && uv run python manage.py spectacular --file openapi.yaml   # drf-spectacular
cd ../web && pnpm gen:api                                               # openapi-typescript → src/api/schema.d.ts
```
Un test falla si `openapi.yaml` no está al día.

## Despliegue
`cp apps/api/.env.example apps/api/.env` (define `DATABASE_URL` del PostgreSQL **externo**, `SECRET_KEY`, `RESEND_*`) y `docker compose up -d --build`.
Web en :3000; admin interno de Django en `127.0.0.1:8000/admin` (crear negocio, menú, programa y personal; `createsuperuser` dentro del contenedor).
