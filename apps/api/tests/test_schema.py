from pathlib import Path

import yaml
from django.core.management import call_command

COMMITTED = Path(__file__).resolve().parent.parent / "openapi.yaml"


def test_committed_openapi_is_up_to_date(tmp_path):
    out = tmp_path / "openapi.yaml"
    call_command("spectacular", file=str(out), validate=True, fail_on_warn=True)
    assert yaml.safe_load(out.read_text(encoding="utf-8")) == yaml.safe_load(COMMITTED.read_text(encoding="utf-8")), (
        "Regenera con: uv run python manage.py spectacular --file openapi.yaml && pnpm --dir ../web gen:api"
    )
