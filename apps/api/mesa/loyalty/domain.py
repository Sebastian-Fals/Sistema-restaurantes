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
    reward: RewardState | None  # recompensa que esta compra completó


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
    stamps: int, rules: Rules, earned: RewardState | None, last_reward: RewardState | None
) -> tuple[int, RewardState | None]:
    """Devuelve (sellos nuevos, recompensa a anular). Escala a soporte si ya se consumió.

    shortcut: el reverso descuenta de la tarjeta actual, no del "lote" exacto de la compra;
    mantiene el total correcto. Si se necesita trazabilidad por lote, modelar sellos como filas.
    """
    if earned is not None:
        reward = earned
    elif stamps > 0:
        return stamps - 1, None
    else:
        reward = last_reward  # el sello de esta compra ya se había convertido en recompensa
    if reward is None or reward.status == "redeemed":
        raise NeedsSupport("La recompensa derivada ya fue usada: escalar a soporte.")
    new_stamps = stamps + rules.stamps_required - 1
    if new_stamps >= rules.stamps_required:
        raise NeedsSupport("El reverso reabre la tarjeta más allá de una recompensa: escalar a soporte.")
    return new_stamps, reward
