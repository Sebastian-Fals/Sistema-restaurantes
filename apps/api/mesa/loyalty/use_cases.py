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
            self.repo.lock_business(business_id)
            customer_id = self.repo.customer_id_by_email(customer_email.strip().lower())
            if customer_id is None:
                raise d.UnknownCustomer("No hay una cuenta con ese correo.")

            existing = self.repo.purchase_by_reference(business_id, reference)
            if existing:
                if (existing.customer_id, existing.amount_cop) != (customer_id, amount_cop):
                    raise d.ReferenceConflict("La referencia ya se usó en otra compra.")
                return PurchaseResult(existing.id, created=False)
            program = self.repo.program(business_id)
            if program is None or not program.active:
                raise d.NoActiveProgram("El negocio no tiene un programa de sellos activo.")
            if not d.is_eligible(amount_cop, program.rules):
                raise d.NotEligible(f"La compra mínima es COP {program.rules.min_purchase_cop}.")
            card = self.repo.lock_card(business_id, customer_id)
            if self.repo.pending_stamp_count(business_id, customer_id) != card.stamps:
                raise d.NeedsSupport("El historial anterior de sellos requiere revisión de soporte.")

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
            self.repo.lock_business(business_id)
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
            self.repo.lock_business(business_id)
            purchase = self.repo.purchase_for_update(business_id, purchase_id)
            if purchase is None:
                raise d.PurchaseNotFound("Compra no encontrada.")
            if purchase.reversed:
                raise d.AlreadyReversed("La compra ya fue reversada.")
            if not purchase.traceable:
                raise d.NeedsSupport("No hay trazabilidad suficiente del sello histórico: escalar a soporte.")
            program = self.repo.program(business_id)
            card = self.repo.lock_card(business_id, purchase.customer_id)
            if program is None or self.repo.pending_stamp_count(business_id, purchase.customer_id) != card.stamps:
                raise d.NeedsSupport("El historial de sellos requiere revisión de soporte.")
            count = self.repo.contribution_count(purchase.reward.id) if purchase.reward else 0
            stamps, to_void = d.reverse_stamp(card.stamps, program.rules, purchase.reward, count)
            if to_void:
                self.repo.mark_voided(to_void.id)
                self.repo.release_reward_stamps(to_void.id)
            self.repo.save_stamps(card.id, stamps)
            self.repo.add_reversal(purchase_id, reason, admin_id)


class ActivateCard(_UseCase):
    def __call__(self, business_id: int, customer_id: int) -> d.CardState:
        """El cliente activa su tarjeta (vacía). Repetirlo devuelve la misma tarjeta."""
        with self.repo.atomic():
            self.repo.lock_business(business_id)
            program = self.repo.program(business_id)
            if program is None or not program.active:
                raise d.NoActiveProgram("El negocio no tiene programa activo.")
            return self.repo.get_or_create_card(business_id, customer_id)


class LookupCustomer(_UseCase):
    def __call__(self, business_id: int, query: str) -> int:
        """Id del cliente buscado por correo o por código de tarjeta de ESTE negocio."""
        email, code = d.parse_customer_query(query)
        if email:
            customer_id = self.repo.customer_id_by_email(email)
        else:
            customer_id = self.repo.customer_id_by_card_code(business_id, code) if code else None
        if customer_id is None or self.repo.program(business_id) is None:
            raise d.UnknownCustomer("No encontramos un cliente con ese código o correo.")
        return customer_id


class SetConsent(_UseCase):
    def __call__(self, business_id: int, customer_id: int, granted: bool) -> None:
        self.repo.set_consent(business_id, customer_id, "email", granted)


class DeleteAccount(_UseCase):
    def __call__(self, customer_id: int) -> None:
        """Anonimiza la cuenta; las compras se conservan sin dato personal."""
        with self.repo.atomic():
            self.repo.anonymize_customer(customer_id)
