import os

os.environ.setdefault("SECRET_KEY", "test-only")
os.environ.setdefault("DATABASE_URL", "sqlite://:memory:")
os.environ["MAIL_ADAPTER"] = "console"

from .settings import *  # noqa: E402,F401,F403
