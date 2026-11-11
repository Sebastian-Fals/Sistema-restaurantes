"""Reglas puras del programa de sellos: sin Django, sin I/O."""

from dataclasses import dataclass
from datetime import datetime

from mesa.errors import DomainError


class NoActiveProgram(DomainError):
    code = "no_active_program"


class UnknownCustomer(DomainError):
    code = "unknown_customer"


class NotEligible(DomainError):
    code = "below_minimum"


class ReferenceConflict(DomainError):
    code = "reference_conflict"


class RewardNotFound(DomainError):
    code = "reward_not_found"


class RewardNotRedeemable(DomainError):
    code = "reward_not_redeemable"


class PurchaseNotFound(DomainError):
    code = "purchase_not_found"


class AlreadyReversed(DomainError):
    code = "already_reversed"


class NeedsSupport(DomainError):
    code = "needs_support"


@dataclass(frozen=True)
class Rules:
    min_purchase_cop: int
    stamps_required: int
    reward_valid_days: int


@dataclass(frozen=True)
class ProgramState:
    rules: Rules
    active: bool


@dataclass(frozen=True)
class RewardState:
    id: int
    status: str  # available | redeemed | voided
    expires_at: datetime


@dataclass(frozen=True)
class PurchaseState:
    id: int
    customer_id: int
    amount_cop: int
    reversed: bool
    reward: RewardState | None  # recompensa a la que contribuyó este sello
    traceable: bool = True


@dataclass(frozen=True)
class CardState:
    id: int
    stamps: int


def is_eligible(amount_cop: int, rules: Rules) -> bool:
    return amount_cop >= rules.min_purchase_cop


def add_stamp(stamps: int, rules: Rules) -> tuple[int, bool]:
    """Un sello por compra. Devuelve (sellos restantes, ¿se ganó recompensa?)."""
    stamps += 1
    return (0, True) if stamps >= rules.stamps_required else (stamps, False)


def reverse_stamp(
    stamps: int, rules: Rules, earned: RewardState | None, contribution_count: int
) -> tuple[int, RewardState | None]:
    """Revierte el sello exacto; nunca toma prestado un sello de otro ciclo."""
    if earned is None:
        if stamps < 1:
            raise NeedsSupport("El historial de sellos requiere revisión de soporte.")
        return stamps - 1, None
    if earned.status != "available":
        raise NeedsSupport("La recompensa derivada ya fue usada: escalar a soporte.")
    new_stamps = stamps + contribution_count - 1
    if new_stamps >= rules.stamps_required:
        raise NeedsSupport("El reverso reabre la tarjeta más allá de una recompensa: escalar a soporte.")
    return new_stamps, earned


def parse_customer_query(q: str) -> tuple[str | None, str | None]:
    """Interpreta la búsqueda del personal: (correo, código de 6 dígitos). Ej. "OLI · 482 916" -> código."""
    q = q.strip().lower()
    if "@" in q:
        return q, None
    digits = "".join(ch for ch in q if ch.isdigit())
    return None, (digits if len(digits) == 6 else None)
