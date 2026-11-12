"""Regressions for exact stamp provenance and safe request retries."""
import importlib

import pytest
from django.apps import apps
from django.db import connection

from mesa.loyalty import models as m
from .conftest import buy, make_user

pytestmark = pytest.mark.django_db


def complete(staff, customer, prefix="T"):
    return [buy(staff, "olivo", customer.email, f"{prefix}-{i}").json()["purchase"]["id"] for i in range(3)]


@pytest.mark.parametrize("purchase_index", [0, 1, 2])
def test_old_redeemed_cycle_is_never_reversed_using_new_stamps(staff, admin, customer, purchase_index):
    ids = complete(staff, customer)
    reward = m.Reward.objects.get()
    assert staff.post(f"/api/v1/b/olivo/rewards/{reward.id}/redeem").status_code == 204
    buy(staff, "olivo", customer.email, "new-cycle")
    result = admin.post(f"/api/v1/b/olivo/purchases/{ids[purchase_index]}/reverse", {"reason": "error"}, format="json")
    assert result.status_code == 409 and result.json()["code"] == "needs_support"
    assert m.Card.objects.get().stamps == 1
    assert not m.PurchaseReversal.objects.exists()
    reward.refresh_from_db()
    assert reward.status == m.Reward.REDEEMED


def test_reverse_contributing_purchase_voids_exact_reward(staff, admin, customer):
    ids = complete(staff, customer)
    first = m.Reward.objects.get()
    complete(staff, customer, "second")
    second = m.Reward.objects.exclude(pk=first.pk).get()
    result = admin.post(f"/api/v1/b/olivo/purchases/{ids[0]}/reverse", {"reason": "error"}, format="json")
    assert result.status_code == 204
    first.refresh_from_db(); second.refresh_from_db()
    assert first.status == m.Reward.VOIDED and second.status == m.Reward.AVAILABLE
    assert m.Card.objects.get().stamps == 2
    assert m.StampContribution.objects.filter(reward=second).count() == 3


def test_released_stamps_can_complete_a_new_reward(staff, admin, customer):
    ids = complete(staff, customer)
    admin.post(f"/api/v1/b/olivo/purchases/{ids[0]}/reverse", {"reason": "error"}, format="json")
    new = buy(staff, "olivo", customer.email, "replacement")
    assert new.status_code == 201 and new.json()["stamps"] == 0
    reward = m.Reward.objects.get(status=m.Reward.AVAILABLE)
    assert set(reward.contributions.values_list("purchase_id", flat=True)) == {ids[1], ids[2], new.json()["purchase"]["id"]}
    staff.post(f"/api/v1/b/olivo/rewards/{reward.id}/redeem")
    result = admin.post(f"/api/v1/b/olivo/purchases/{ids[1]}/reverse", {"reason": "error"}, format="json")
    assert result.status_code == 409 and result.json()["code"] == "needs_support"


def test_complex_reversal_escalates_without_voiding_unrelated_reward(staff, admin, customer):
    ids = complete(staff, customer)
    buy(staff, "olivo", customer.email, "next")
    result = admin.post(f"/api/v1/b/olivo/purchases/{ids[0]}/reverse", {"reason": "error"}, format="json")
    assert result.status_code == 409 and result.json()["code"] == "needs_support"
    assert m.Card.objects.get().stamps == 1
    assert m.Reward.objects.get().status == m.Reward.AVAILABLE
    assert not m.PurchaseReversal.objects.exists()


def test_replay_returns_existing_purchase_when_program_is_inactive(staff, customer, olivo):
    original = buy(staff, "olivo", customer.email, "existing").json()
    m.Program.objects.filter(business=olivo).update(is_active=False)
    replay = buy(staff, "olivo", customer.email, "existing")
    assert replay.status_code == 200 and replay.json()["created"] is False
    assert replay.json()["purchase"] == original["purchase"]
    assert m.Purchase.objects.count() == 1 and m.Card.objects.get().stamps == 1
    assert buy(staff, "olivo", customer.email, "new").json()["code"] == "no_active_program"


def test_conflicting_reference_does_not_create_another_customers_card(staff, customer):
    buy(staff, "olivo", customer.email, "existing")
    other = make_user("other@example.com")
    conflict = buy(staff, "olivo", other.email, "existing")
    assert conflict.status_code == 409 and conflict.json()["code"] == "reference_conflict"
    assert m.Purchase.objects.count() == 1
    assert not m.Card.objects.filter(customer=other).exists()


def test_unknown_legacy_stamp_cannot_be_reversed_or_silently_consumed(staff, admin, customer):
    pid = buy(staff, "olivo", customer.email, "legacy").json()["purchase"]["id"]
    m.StampContribution.objects.all().delete()  # provenance missing in old data
    reverse = admin.post(f"/api/v1/b/olivo/purchases/{pid}/reverse", {"reason": "error"}, format="json")
    assert reverse.status_code == 409 and reverse.json()["code"] == "needs_support"
    purchase = buy(staff, "olivo", customer.email, "new")
    assert purchase.status_code == 409 and purchase.json()["code"] == "needs_support"
    assert m.Purchase.objects.count() == 1 and m.Card.objects.get().stamps == 1


def test_backfill_restores_completed_cycles_and_pending_stamps(staff, customer):
    ids = complete(staff, customer)
    pending = buy(staff, "olivo", customer.email, "pending").json()["purchase"]["id"]
    reward = m.Reward.objects.get()
    m.StampContribution.objects.all().delete()
    # The backfill only needs the connection alias, not any DDL.
    from types import SimpleNamespace
    migration = importlib.import_module("mesa.loyalty.migrations.0002_stamp_contributions")
    migration.backfill_unambiguous_stamps(apps, SimpleNamespace(connection=connection))
    assert set(reward.contributions.values_list("purchase_id", flat=True)) == set(ids)
    assert m.StampContribution.objects.get(purchase_id=pending).reward_id is None


def test_backfill_leaves_ambiguous_reversal_history_for_support(staff, admin, customer):
    pid = buy(staff, "olivo", customer.email, "old").json()["purchase"]["id"]
    admin.post(f"/api/v1/b/olivo/purchases/{pid}/reverse", {"reason": "error"}, format="json")
    buy(staff, "olivo", customer.email, "new")
    m.StampContribution.objects.all().delete()
    from types import SimpleNamespace
    migration = importlib.import_module("mesa.loyalty.migrations.0002_stamp_contributions")
    migration.backfill_unambiguous_stamps(apps, SimpleNamespace(connection=connection))
    assert not m.StampContribution.objects.exists()
