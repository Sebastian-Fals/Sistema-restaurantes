"""Casos de uso (comandos). Dependen solo de dominio y puertos."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.utils import timezone

from . import domain as d
from .ports import LoyaltyRepository


@dataclass(frozen=True)
class PurchaseResult:
    purchase_id: int
    created: bool  # False => reintento idempotente: se devuelve el resultado original


class _UseCase:
    def __init__(self, repo: LoyaltyRepository, clock: Callable[[], datetime] = timezone.now):
        self.repo, self.clock = repo, clock


class RegisterPurchase(_UseCase):
    def __call__(
        self, business_id: int, staff_id: int, customer_email: str, amount_cop: int, reference: str
    ) -> PurchaseResult:
        with self.repo.atomic():
            program = self.repo.program(business_id)
            if program is None or not program.active:
                raise d.NoActiveProgram("El negocio no tiene un programa de sellos activo.")
            customer_id = self.repo.customer_id_by_email(customer_email.strip().lower())
            if customer_id is None:
                raise d.UnknownCustomer("No hay una cuenta con ese correo.")

            card = self.repo.lock_card(business_id, customer_id)  # serializa operaciones del mismo cliente
            existing = self.repo.purchase_by_reference(business_id, reference)
            if existing:
                if (existing.customer_id, existing.amount_cop) != (customer_id, amount_cop):
                    raise d.ReferenceConflict("La referencia ya se usó en otra compra.")
                return PurchaseResult(existing.id, created=False)
            if not d.is_eligible(amount_cop, program.rules):
                raise d.NotEligible(f"La compra mínima es COP {program.rules.min_purchase_cop}.")

            purchase = self.repo.add_purchase(business_id, customer_id, amount_cop, reference, staff_id)
            stamps, earned = d.add_stamp(card.stamps, program.rules)
            self.repo.save_stamps(card.id, stamps)
            if earned:
                expires = self.clock() + timedelta(days=program.rules.reward_valid_days)
                self.repo.add_reward(business_id, customer_id, purchase.id, expires)
            return PurchaseResult(purchase.id, created=True)


class RedeemReward(_UseCase):
    def __call__(self, business_id: int, staff_id: int, reward_id: int) -> None:
        with self.repo.atomic():
            reward = self.repo.reward_for_update(business_id, reward_id)
            if reward is None:
                raise d.RewardNotFound("Recompensa no encontrada.")
            if reward.status != "available":
                raise d.RewardNotRedeemable("La recompensa ya fue usada o anulada.")
            now = self.clock()
            if reward.expires_at <= now:
                raise d.RewardNotRedeemable("La recompensa venció.")
            self.repo.mark_redeemed(reward_id, staff_id, now)


class ReversePurchase(_UseCase):
    def __call__(self, business_id: int, admin_id: int, purchase_id: int, reason: str) -> None:
        with self.repo.atomic():
            purchase = self.repo.purchase_for_update(business_id, purchase_id)
            if purchase is None:
                raise d.PurchaseNotFound("Compra no encontrada.")
            if purchase.reversed:
                raise d.AlreadyReversed("La compra ya fue reversada.")
            program = self.repo.program(business_id)
            card = self.repo.lock_card(business_id, purchase.customer_id)
            last = self.repo.latest_reward(business_id, purchase.customer_id)
            stamps, to_void = d.reverse_stamp(card.stamps, program.rules, purchase.reward, last)
            if to_void:
                self.repo.mark_voided(to_void.id)
            self.repo.save_stamps(card.id, stamps)
            self.repo.add_reversal(purchase_id, reason, admin_id)
