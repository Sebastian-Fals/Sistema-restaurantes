import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta

from mesa.errors import DomainError

CODE_TTL = timedelta(minutes=10)
RESEND_COOLDOWN = timedelta(seconds=60)
MAX_ATTEMPTS = 5


class InvalidCode(DomainError):
    code = "invalid_code"


class TooManyRequests(DomainError):
    code = "too_many_requests"


@dataclass(frozen=True)
class PendingCode:
    id: int
    code_hash: str
    attempts: int
    expires_at: datetime


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_code(email: str, code: str, secret: str) -> str:
    return hmac.new(secret.encode(), f"{email}:{code}".encode(), hashlib.sha256).hexdigest()
