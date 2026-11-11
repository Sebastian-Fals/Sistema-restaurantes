"""Isolated local acceptance API. No test-only endpoints or real emails."""
import logging
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

api_root = Path(__file__).resolve().parents[2] / "api"
sys.path.insert(0, str(api_root))

with TemporaryDirectory(prefix="mesa-e2e-") as folder:
    os.environ.update(
        DJANGO_SETTINGS_MODULE="config.settings",
        DATABASE_URL=f"sqlite:///{folder}/acceptance.sqlite3",
        DEBUG="true",
        SECRET_KEY="local-acceptance-only",
        MAIL_ADAPTER="console",
        COOKIE_SECURE="false",
        ALLOWED_HOSTS="127.0.0.1,localhost",
        CSRF_TRUSTED_ORIGINS="http://127.0.0.1:3011",
    )
    import django
    django.setup()
    from django.core.management import call_command
    from mesa.identity.models import User
    from mesa.loyalty.models import Membership, Program

    log_path = Path(os.environ["MESA_E2E_LOG"])
    log_path.write_text("")
    logging.getLogger("mesa.identity.adapters.mailers").addHandler(logging.FileHandler(log_path))
    call_command("migrate", verbosity=0)
    call_command("seed_demo", verbosity=0)
    Program.objects.filter(business__slug="cafe-olivo").update(stamps_required=3)
    user = User.objects.create_user("offline-admin@cafe-olivo.test")
    Membership.objects.create(business=Program.objects.get().business, user=user, role=Membership.ADMIN)
    call_command("runserver", "127.0.0.1:8011", use_reloader=False)
