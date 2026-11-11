import pytest

from mesa.loyalty import models as m

from .conftest import buy, client_for, make_business, make_user

pytestmark = pytest.mark.django_db


def test_purchase_credits_one_stamp(staff, customer):
    r = buy(staff, "olivo", customer.email, "T-1")
    assert r.status_code == 201
    assert r.json()["stamps"] == 1 and r.json()["created"] is True


def test_same_reference_is_idempotent(staff, customer):
    buy(staff, "olivo", customer.email, "T-1")
    r = buy(staff, "olivo", customer.email, "T-1")
    assert r.status_code == 200 and r.json()["created"] is False and r.json()["stamps"] == 1
    assert m.Purchase.objects.count() == 1


def test_reference_reused_for_other_amount_conflicts(staff, customer):
    buy(staff, "olivo", customer.email, "T-1")
    r = buy(staff, "olivo", customer.email, "T-1", amount=99000)
    assert r.status_code == 409 and r.json()["code"] == "reference_conflict"


def test_below_minimum_rejected_without_stamp(staff, customer):
    r = buy(staff, "olivo", customer.email, "T-1", amount=5000)
    assert r.status_code == 422 and r.json()["code"] == "below_minimum"
    assert not m.Purchase.objects.exists()


def test_unknown_customer(staff):
    assert buy(staff, "olivo", "nadie@example.com", "T-1").status_code == 404


def test_reward_earned_and_redeemed_once(staff, customer):
    for i in range(3):
        r = buy(staff, "olivo", customer.email, f"T-{i}")
    assert r.json()["stamps"] == 0
    reward = m.Reward.objects.get()
    assert staff.post(f"/api/v1/b/olivo/rewards/{reward.id}/redeem").status_code == 204
    again = staff.post(f"/api/v1/b/olivo/rewards/{reward.id}/redeem")
    assert again.status_code == 409 and again.json()["code"] == "reward_not_redeemable"


def test_expired_reward_cannot_be_redeemed(staff, customer):
    from datetime import timedelta
    from django.utils import timezone

    for i in range(3):
        buy(staff, "olivo", customer.email, f"T-{i}")
    m.Reward.objects.update(expires_at=timezone.now() - timedelta(days=1))
    assert staff.post(f"/api/v1/b/olivo/rewards/{m.Reward.objects.get().id}/redeem").status_code == 409


def test_tenant_isolation(staff, customer):
    other = make_business("otro")
    outsider = client_for(make_user("x@otro.co", other, m.Membership.ADMIN))
    # personal de otro negocio no opera en Olivo
    assert buy(outsider, "olivo", customer.email, "T-1").status_code == 403
    assert outsider.get("/api/v1/b/olivo/summary").status_code == 403
    # y un id de recompensa/compra de otro negocio no es accesible por la URL propia
    for i in range(3):
        buy(staff, "olivo", customer.email, f"T-{i}")
    reward_id, purchase_id = m.Reward.objects.get().id, m.Purchase.objects.first().id
    assert outsider.post(f"/api/v1/b/otro/rewards/{reward_id}/redeem").status_code == 404
    assert outsider.post(f"/api/v1/b/otro/purchases/{purchase_id}/reverse", {"reason": "x"}, format="json").status_code == 404


def test_staff_cannot_reverse_or_see_summary(staff):
    assert staff.get("/api/v1/b/olivo/summary").status_code == 403
    assert staff.post("/api/v1/b/olivo/purchases/1/reverse", {"reason": "x"}, format="json").status_code == 403


def test_reverse_removes_stamp_and_keeps_history(staff, admin, customer):
    pid = buy(staff, "olivo", customer.email, "T-1").json()["purchase"]["id"]
    assert admin.post(f"/api/v1/b/olivo/purchases/{pid}/reverse", {"reason": "error de digitación"}, format="json").status_code == 204
    assert m.Card.objects.get().stamps == 0
    assert m.Purchase.objects.filter(pk=pid).exists()  # no se borra
    again = admin.post(f"/api/v1/b/olivo/purchases/{pid}/reverse", {"reason": "otra vez"}, format="json")
    assert again.status_code == 409 and again.json()["code"] == "already_reversed"


def test_reverse_completing_purchase_voids_reward(staff, admin, customer):
    ids = [buy(staff, "olivo", customer.email, f"T-{i}").json()["purchase"]["id"] for i in range(3)]
    assert admin.post(f"/api/v1/b/olivo/purchases/{ids[-1]}/reverse", {"reason": "devolución"}, format="json").status_code == 204
    assert m.Reward.objects.get().status == m.Reward.VOIDED
    assert m.Card.objects.get().stamps == 2


def test_reverse_after_redeemed_escalates(staff, admin, customer):
    ids = [buy(staff, "olivo", customer.email, f"T-{i}").json()["purchase"]["id"] for i in range(3)]
    staff.post(f"/api/v1/b/olivo/rewards/{m.Reward.objects.get().id}/redeem")
    r = admin.post(f"/api/v1/b/olivo/purchases/{ids[-1]}/reverse", {"reason": "x"}, format="json")
    assert r.status_code == 409 and r.json()["code"] == "needs_support"
    assert not m.PurchaseReversal.objects.exists()


def test_customer_card_and_consent(staff, customer):
    c = client_for(customer)
    assert c.post("/api/v1/b/olivo/card").status_code == 200
    buy(staff, "olivo", customer.email, "T-1")
    card = c.get("/api/v1/me/cards").json()[0]
    assert card["stamps"] == 1 and card["stamps_required"] == 3 and card["marketing_consent"] is False
    c.put("/api/v1/b/olivo/consent", {"granted": True}, format="json")
    assert c.get("/api/v1/me/cards").json()[0]["marketing_consent"] is True


def test_public_page_needs_no_login(olivo):
    from rest_framework.test import APIClient

    body = APIClient().get("/api/v1/public/b/olivo").json()
    assert body["program"]["stamps_required"] == 3 and body["menu"] == []


def test_summary_and_activity(staff, admin, customer):
    for i in range(3):
        buy(staff, "olivo", customer.email, f"T-{i}")
    s = admin.get("/api/v1/b/olivo/summary").json()
    assert s["purchases"] == 3 and s["rewards_earned"] == 1 and s["rewards_available"] == 1 and s["customers"] == 1
    types = [e["type"] for e in admin.get("/api/v1/b/olivo/activity").json()]
    assert types.count("purchase") == 3
    assert admin.get("/api/v1/b/olivo/activity?type=redemption").json() == []


def test_delete_account_anonymizes(customer):
    c = client_for(customer)
    assert c.delete("/api/v1/me").status_code == 204
    customer.refresh_from_db()
    assert not customer.is_active and customer.email.startswith("eliminado-")


def test_summary_counts_returning_customers_and_daily_series(staff, admin, customer):
    other = make_user("luis@example.com")
    buy(staff, "olivo", customer.email, "T-1")
    buy(staff, "olivo", customer.email, "T-2")
    buy(staff, "olivo", other.email, "T-3")
    s = admin.get("/api/v1/b/olivo/summary").json()
    assert s["returning_customers"] == 1
    assert len(s["daily"]) == 7 and s["daily"][-1]["stamps"] == 3 and sum(d["stamps"] for d in s["daily"]) == 3


def test_lookup_by_customer_code_is_scoped_to_business(staff, customer):
    client_for(customer).post("/api/v1/b/olivo/card")
    card = m.Card.objects.get(customer=customer)
    assert len(card.code) == 6 and card.display_code.startswith("OLI · ")
    found = staff.get("/api/v1/b/olivo/customer", {"q": card.display_code}).json()
    assert found["email"] == customer.email and found["customer_code"] == card.display_code
    assert staff.get("/api/v1/b/olivo/customer", {"q": customer.email}).status_code == 200

    other = make_business("otro")
    m.Card.objects.create(business=other, customer=make_user("x@example.com"), code="999999")
    assert staff.get("/api/v1/b/olivo/customer", {"q": "999999"}).status_code == 404


def test_activate_card_twice_returns_same_card(customer, olivo):
    c = client_for(customer)
    first, second = c.post("/api/v1/b/olivo/card").json(), c.post("/api/v1/b/olivo/card").json()
    assert first["customer_code"] == second["customer_code"] and m.Card.objects.filter(customer=customer).count() == 1


def test_activate_card_without_active_program_conflicts(customer, olivo):
    m.Program.objects.filter(business=olivo).update(is_active=False)
    r = client_for(customer).post("/api/v1/b/olivo/card")
    assert r.status_code == 409 and r.json()["code"] == "no_active_program"


def test_card_creation_race_reads_existing_card(customer, olivo, monkeypatch):
    """Otra petición creó la tarjeta tras nuestra lectura: el INSERT viola uniq_card y se devuelve la existente."""
    from django.db.models.query import QuerySet

    from mesa.loyalty.adapters.orm import DjangoLoyaltyRepository

    existing = m.Card.objects.create(business=olivo, customer=customer)
    real_first, stale = QuerySet.first, [True]

    def first_misses_once(qs):  # la primera lectura aún no ve la tarjeta de la otra petición
        if qs.model is m.Card and stale:
            stale.pop()
            return None
        return real_first(qs)

    monkeypatch.setattr(QuerySet, "first", first_misses_once)
    card = DjangoLoyaltyRepository().get_or_create_card(olivo.id, customer.id)
    assert card.id == existing.id and m.Card.objects.filter(customer=customer).count() == 1
