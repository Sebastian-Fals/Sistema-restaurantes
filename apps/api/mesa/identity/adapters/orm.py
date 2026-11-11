from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import F

from mesa.identity.domain import InvalidCode, PendingCode
from mesa.identity.models import LoginCode, User


class DjangoLoginCodeStore:
    def last_created_at(self, email):
        return LoginCode.objects.filter(email=email).order_by("-created_at", "-id").values_list("created_at", flat=True).first()

    def add(self, email, code_hash, created_at, expires_at):
        with transaction.atomic():
            LoginCode.objects.filter(email=email, used=False).update(used=True)
            LoginCode.objects.create(email=email, code_hash=code_hash, created_at=created_at, expires_at=expires_at)

    def latest_pending(self, email, now):
        # A consumed/expired latest issuance must never expose an older code.
        row = LoginCode.objects.filter(email=email).order_by("-created_at", "-id").first()
        if row is None or row.used or row.expires_at <= now:
            return None
        return PendingCode(row.id, row.code_hash, row.attempts, row.expires_at)

    def register_attempt(self, code_id):
        LoginCode.objects.filter(pk=code_id).update(attempts=F("attempts") + 1)

    def consume(self, code_id):
        return LoginCode.objects.filter(pk=code_id, used=False).update(used=True) == 1


class DjangoUserDirectory:
    def get_or_create(self, email):
        user, _ = User.objects.get_or_create(email=email, defaults={"password": lambda: make_password(None)})
        if not user.is_active:
            raise InvalidCode("Código inválido o vencido.")
        return user.pk
