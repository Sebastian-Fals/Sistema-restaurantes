"""Consultas (lado lectura). Siempre acotadas a un negocio."""

from collections import Counter
from datetime import date, datetime, time, timedelta

from django.db.models import Count
from django.utils import timezone

from .models import Card, Purchase, PurchaseReversal, Reward


def day_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    tz = timezone.get_current_timezone()
    return (
        datetime.combine(start, time.min, tz),
        datetime.combine(end + timedelta(days=1), time.min, tz),
    )


def summary(business, start: date, end: date) -> dict:
    lo, hi = day_bounds(start, end)
    purchases = Purchase.objects.filter(business=business, created_at__gte=lo, created_at__lt=hi, reversal__isnull=True)
    rewards = Reward.objects.filter(business=business).exclude(status=Reward.VOIDED)
    week_lo, _ = day_bounds(end - timedelta(days=6), end)
    per_day = Counter(
        timezone.localdate(at)
        for at in Purchase.objects.filter(
            business=business, created_at__gte=week_lo, created_at__lt=hi, reversal__isnull=True
        ).values_list("created_at", flat=True)
    )
    return {
        "returning_customers": purchases.values("customer").annotate(n=Count("id")).filter(n__gte=2).count(),
        "daily": [{"date": d, "stamps": per_day[d]} for d in (end - timedelta(days=i) for i in range(6, -1, -1))],
        "customers": Card.objects.filter(business=business).count(),
        "purchases": purchases.count(),
        "stamps_credited": purchases.count(),  # una compra elegible = un sello
        "rewards_earned": rewards.filter(earned_at__gte=lo, earned_at__lt=hi).count(),
        "rewards_redeemed": rewards.filter(redeemed_at__gte=lo, redeemed_at__lt=hi).count(),
        "rewards_available": rewards.filter(status=Reward.AVAILABLE, expires_at__gt=timezone.now()).count(),
    }


def activity(business, start: date, end: date, kind: str | None, limit: int = 200) -> list[dict]:
    lo, hi = day_bounds(start, end)
    events = []
    if kind in (None, "purchase"):
        for p in Purchase.objects.filter(business=business, created_at__gte=lo, created_at__lt=hi).select_related(
            "customer", "registered_by"
        )[:limit]:
            events.append(
                dict(type="purchase", at=p.created_at, actor_email=p.registered_by.email, customer_email=p.customer.email,
                     amount_cop=p.amount_cop, detail="", purchase_id=p.id)
            )
    if kind in (None, "reversal"):
        for r in PurchaseReversal.objects.filter(
            purchase__business=business, created_at__gte=lo, created_at__lt=hi
        ).select_related("purchase__customer", "reversed_by")[:limit]:
            events.append(
                dict(type="reversal", at=r.created_at, actor_email=r.reversed_by.email,
                     customer_email=r.purchase.customer.email, amount_cop=r.purchase.amount_cop,
                     detail=r.reason, purchase_id=r.purchase_id)
            )
    if kind in (None, "redemption"):
        for w in Reward.objects.filter(
            business=business, status=Reward.REDEEMED, redeemed_at__gte=lo, redeemed_at__lt=hi
        ).select_related("customer", "redeemed_by")[:limit]:
            events.append(
                dict(type="redemption", at=w.redeemed_at, actor_email=w.redeemed_by.email,
                     customer_email=w.customer.email, amount_cop=None, detail="", purchase_id=w.purchase_id)
            )
    return sorted(events, key=lambda e: e["at"], reverse=True)[:limit]


def card_view(card: Card) -> dict:
    """Tarjeta del cliente con recompensas y actividad reciente."""
    b = card.business
    now = timezone.now()
    rewards = [
        r for r in Reward.objects.filter(business=b, customer=card.customer, status=Reward.AVAILABLE) if r.expires_at > now
    ]
    return {
        "customer_code": card.display_code,
        "business_slug": b.slug,
        "business_name": b.name,
        "reward_name": b.program.reward_name,
        "stamps": card.stamps,
        "stamps_required": b.program.stamps_required,
        "rewards": rewards,
        "recent_purchases": Purchase.objects.filter(business=b, customer=card.customer).select_related("reversal")[:10],
        "marketing_consent": b.consent_set.filter(customer=card.customer, channel="email", granted=True).exists(),
    }
