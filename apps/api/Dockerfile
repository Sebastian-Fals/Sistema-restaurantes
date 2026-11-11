FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY . .
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
# collectstatic no necesita BD real; se usa una URL ficticia solo en build.
RUN DATABASE_URL=postgres://build:build@localhost/build SECRET_KEY=build python manage.py collectstatic --noinput
RUN useradd --system --uid 10001 mesa
USER mesa
EXPOSE 8000
# Migra al arrancar (idempotente) y sirve con gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi -b 0.0.0.0:8000 --workers 3 --access-logfile -"]
