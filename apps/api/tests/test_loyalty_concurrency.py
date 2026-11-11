"""Real row-lock regressions; executed against PostgreSQL by the API CI job."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.db import close_old_connections, connection

from mesa.errors import DomainError
from mesa.loyalty import models as m
from mesa.loyalty.adapters.orm import DjangoLoyaltyRepository
from mesa.loyalty.use_cases import RedeemReward, RegisterPurchase, ReversePurchase
from .conftest import make_business, make_user

pytestmark = [pytest.mark.django_db(transaction=True),
              pytest.mark.skipif(connection.vendor != "postgresql", reason="requires PostgreSQL row locks")]


def concurrent(*operations):
    ready = Barrier(len(operations))

    def run(operation):
        close_old_connections()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET lock_timeout TO '5s'")
                cursor.execute("SET statement_timeout TO '10s'")
            ready.wait(timeout=5)
            try:
                return operation(DjangoLoyaltyRepository())
            except DomainError as error:
                return error.code
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=len(operations)) as pool:
        futures = [pool.submit(run, operation) for operation in operations]
        return [future.result(timeout=15) for future in futures]


def setup(stamps_required=3):
    business = make_business(stamps_required=stamps_required)
    actor = make_user("staff@example.com", business, m.Membership.ADMIN)
    customer = make_user("customer@example.com")
    return business.id, actor.id, customer


def test_same_reference_same_customer_credits_once():
    business, actor, customer = setup()
    def register(repo):
        return RegisterPurchase(repo)(business, actor, customer.email, 15000, "same")
    results = concurrent(register, register)
    assert sorted(r.created for r in results) == [False, True]
    assert results[0].purchase_id == results[1].purchase_id
    assert m.Purchase.objects.count() == 1 and m.Card.objects.get().stamps == 1


def test_same_reference_different_customers_conflicts_without_side_effects():
    business, actor, customer = setup()
    other = make_user("other@example.com")
    results = concurrent(
        lambda repo: RegisterPurchase(repo)(business, actor, customer.email, 15000, "same"),
        lambda repo: RegisterPurchase(repo)(business, actor, other.email, 15000, "same"),
    )
    assert sum(r == "reference_conflict" for r in results) == 1
    assert m.Purchase.objects.count() == 1 and m.Card.objects.count() == 1
    assert m.Card.objects.get().stamps == 1


def test_concurrent_purchases_complete_one_exact_reward():
    business, actor, customer = setup(stamps_required=2)
    results = concurrent(
        lambda repo: RegisterPurchase(repo)(business, actor, customer.email, 15000, "first"),
        lambda repo: RegisterPurchase(repo)(business, actor, customer.email, 15000, "second"),
    )
    assert all(r.created for r in results)
    assert m.Card.objects.get().stamps == 0
    assert m.Reward.objects.count() == 1
    assert m.Reward.objects.get().contributions.count() == 2


def test_concurrent_redemption_consumes_once():
    business, actor, customer = setup(stamps_required=1)
    RegisterPurchase(DjangoLoyaltyRepository())(business, actor, customer.email, 15000, "first")
    reward = m.Reward.objects.get()
    results = concurrent(
        lambda repo: RedeemReward(repo)(business, actor, reward.id),
        lambda repo: RedeemReward(repo)(business, actor, reward.id),
    )
    assert results.count(None) == 1 and results.count("reward_not_redeemable") == 1
    reward.refresh_from_db()
    assert reward.status == m.Reward.REDEEMED and reward.redeemed_by_id == actor


def test_redemption_and_reversal_cannot_both_succeed_or_deadlock():
    business, actor, customer = setup(stamps_required=1)
    purchase = RegisterPurchase(DjangoLoyaltyRepository())(business, actor, customer.email, 15000, "first")
    reward = m.Reward.objects.get()
    results = concurrent(
        lambda repo: RedeemReward(repo)(business, actor, reward.id),
        lambda repo: ReversePurchase(repo)(business, actor, purchase.purchase_id, "mistake"),
    )
    assert results.count(None) == 1
    assert any(r in ("needs_support", "reward_not_redeemable") for r in results)
    reward.refresh_from_db()
    assert (reward.status, m.PurchaseReversal.objects.count()) in [(m.Reward.REDEEMED, 0), (m.Reward.VOIDED, 1)]
