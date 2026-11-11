import hmac
import secrets
from collections.abc import Callable
from datetime import datetime

from django.utils import timezone

from . import domain as d
from .ports import LoginCodeStore, Mailer, UserDirectory


class RequestLoginCode:
    def __init__(
        self,
        store: LoginCodeStore,
        mailer: Mailer,
        secret: str,
        clock: Callable[[], datetime] = timezone.now,
        generate: Callable[[], str] = lambda: f"{secrets.randbelow(10**6):06d}",
    ):
        self.store, self.mailer, self.secret, self.clock, self.generate = store, mailer, secret, clock, generate

    def __call__(self, email: str) -> None:
        email, now = d.normalize_email(email), self.clock()
        last = self.store.last_created_at(email)
        if last and now - last < d.RESEND_COOLDOWN:
            raise d.TooManyRequests("Espera un minuto antes de pedir otro código.")
        code = self.generate()
        self.store.add(email, d.hash_code(email, code, self.secret), now, now + d.CODE_TTL)
        self.mailer.send_login_code(email, code)


class VerifyLoginCode:
    def __init__(
        self,
        store: LoginCodeStore,
        users: UserDirectory,
        secret: str,
        clock: Callable[[], datetime] = timezone.now,
    ):
        self.store, self.users, self.secret, self.clock = store, users, secret, clock

    def __call__(self, email: str, code: str) -> int:
        """Devuelve el id de usuario (lo crea si es la primera vez)."""
        email = d.normalize_email(email)
        pending = self.store.latest_pending(email, self.clock())
        if pending is None or pending.attempts >= d.MAX_ATTEMPTS:
            raise d.InvalidCode("Código inválido o vencido.")
        if not hmac.compare_digest(pending.code_hash, d.hash_code(email, code.strip(), self.secret)):
            self.store.register_attempt(pending.id)
            raise d.InvalidCode("Código inválido o vencido.")
        if not self.store.consume(pending.id):
            raise d.InvalidCode("Código inválido o vencido.")
        return self.users.get_or_create(email)
