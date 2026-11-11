from datetime import datetime
from typing import Protocol

from .domain import PendingCode


class Mailer(Protocol):
    def send_login_code(self, email: str, code: str) -> None: ...


class LoginCodeStore(Protocol):
    def last_created_at(self, email: str) -> datetime | None: ...
    def add(self, email: str, code_hash: str, created_at: datetime, expires_at: datetime) -> None: ...
    def latest_pending(self, email: str, now: datetime) -> PendingCode | None: ...
    def register_attempt(self, code_id: int) -> None: ...
    def consume(self, code_id: int) -> bool:
        """Marca el código como usado de forma atómica; False si otro proceso ya lo usó."""


class UserDirectory(Protocol):
    def get_or_create(self, email: str) -> int: ...
