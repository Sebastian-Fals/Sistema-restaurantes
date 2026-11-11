from django.db import IntegrityError, transaction

from mesa.identity.models import User
from mesa.loyalty import domain as d
from mesa.loyalty.models import Card, Consent, Program, Purchase, PurchaseReversal, Reward


def _reward(r: Reward | None) -> d.RewardState | None:
    return r and d.RewardState(r.id, r.status, r.expires_at)


def _purchase(p: Purchase) -> d.PurchaseState:
    reward = Reward.objects.filter(purchase=p).first()
    return d.PurchaseState(p.id, p.customer_id, p.amount_cop, PurchaseReversal.objects.filter(purchase=p).exists(), _reward(reward))


class DjangoLoyaltyRepository:
    def atomic(self):
        return transaction.atomic()

    def program(self, business_id):
        p = Program.objects.filter(business_id=business_id).first()
        return p and d.ProgramState(d.Rules(p.min_purchase_cop, p.stamps_required, p.reward_valid_days), p.is_active)

    def customer_id_by_email(self, email):
        return User.objects.filter(email=email, is_active=True).values_list("id", flat=True).first()

    def customer_id_by_card_code(self, business_id, code):
        return (
            Card.objects.filter(business_id=business_id, code=code, customer__is_active=True)
            .values_list("customer_id", flat=True)
            .first()
        )

    def get_or_create_card(self, business_id, customer_id):
        for _ in range(3):
            card = Card.objects.filter(business_id=business_id, customer_id=customer_id).first()
            if card is None:
                try:
                    with transaction.atomic():  # savepoint: el IntegrityError no rompe la transacción externa
                        card = Card.objects.create(business_id=business_id, customer_id=customer_id)
                except IntegrityError:
                    continue  # carrera: otra petición creó esta tarjeta (uniq_card) o tomó el código (uniq_card_code)
            return d.CardState(card.id, card.stamps)
        raise IntegrityError("No se pudo crear la tarjeta tras varios intentos.")

    def lock_card(self, business_id, customer_id):
        self.get_or_create_card(business_id, customer_id)
        card = Card.objects.select_for_update().get(business_id=business_id, customer_id=customer_id)
        return d.CardState(card.id, card.stamps)

    def save_stamps(self, card_id, stamps):
        Card.objects.filter(pk=card_id).update(stamps=stamps)

    def purchase_by_reference(self, business_id, reference):
        p = Purchase.objects.filter(business_id=business_id, reference=reference).first()
        return p and _purchase(p)

    def purchase_for_update(self, business_id, purchase_id):
        p = Purchase.objects.select_for_update().filter(business_id=business_id, pk=purchase_id).first()
        return p and _purchase(p)

    def add_purchase(self, business_id, customer_id, amount_cop, reference, staff_id):
        p = Purchase.objects.create(
            business_id=business_id, customer_id=customer_id, amount_cop=amount_cop,
            reference=reference, registered_by_id=staff_id,
        )
        return _purchase(p)

    def add_reward(self, business_id, customer_id, purchase_id, expires_at):
        return _reward(
            Reward.objects.create(
                business_id=business_id, customer_id=customer_id, purchase_id=purchase_id, expires_at=expires_at
            )
        )

    def latest_reward(self, business_id, customer_id):
        r = (
            Reward.objects.filter(business_id=business_id, customer_id=customer_id)
            .exclude(status=Reward.VOIDED)
            .first()  # orden por defecto: más reciente primero
        )
        return _reward(r)

    def reward_for_update(self, business_id, reward_id):
        return _reward(Reward.objects.select_for_update().filter(business_id=business_id, pk=reward_id).first())

    def mark_redeemed(self, reward_id, staff_id, at):
        Reward.objects.filter(pk=reward_id).update(status=Reward.REDEEMED, redeemed_by_id=staff_id, redeemed_at=at)

    def mark_voided(self, reward_id):
        Reward.objects.filter(pk=reward_id).update(status=Reward.VOIDED)

    def add_reversal(self, purchase_id, reason, admin_id):
        PurchaseReversal.objects.create(purchase_id=purchase_id, reason=reason, reversed_by_id=admin_id)

    def set_consent(self, business_id, customer_id, channel, granted):
        Consent.objects.update_or_create(
            business_id=business_id, customer_id=customer_id, channel=channel, defaults={"granted": granted}
        )

    def anonymize_customer(self, customer_id):
        u = User.objects.get(pk=customer_id)
        u.email, u.is_active = f"eliminado-{u.pk}@invalid.local", False
        u.set_unusable_password()
        u.save()
        Consent.objects.filter(customer_id=customer_id).delete()
