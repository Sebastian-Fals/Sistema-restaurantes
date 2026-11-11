from datetime import timedelta
from types import SimpleNamespace

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from mesa import container
from mesa.identity.models import User
from mesa.loyalty import models as m
from mesa.loyalty import selectors

from . import serializers as s
from .permissions import BusinessScoped, IsBusinessAdmin, IsBusinessStaff

ERRORS = {404: s.ErrorSerializer, 409: s.ErrorSerializer, 422: s.ErrorSerializer}


# ---------- Cuenta y cliente ----------
class MeView(APIView):
    @extend_schema(responses=s.MeSerializer)
    def get(self, request):
        memberships = [
            {"business_slug": ms.business.slug, "role": ms.role}
            for ms in request.user.memberships.select_related("business")
        ]
        return Response({"id": request.user.id, "email": request.user.email, "memberships": memberships})

    @extend_schema(responses={204: None})
    def delete(self, request):
        """Elimina la cuenta: anonimiza el correo; las compras se conservan sin dato personal."""
        u = request.user
        u.email, u.is_active = f"eliminado-{u.pk}@invalid.local", False
        u.set_unusable_password()
        u.save()
        m.Consent.objects.filter(customer=u).delete()
        return Response(status=204)


class PublicBusinessView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: s.PublicBusinessSerializer, 404: s.ErrorSerializer})
    def get(self, request, slug):
        b = get_object_or_404(m.Business, slug=slug, is_active=True)
        view = SimpleNamespace(
            slug=b.slug, name=b.name, description=b.description, address=b.address,
            contact_email=b.contact_email, contact_phone=b.contact_phone,
            program=m.Program.objects.filter(business=b, is_active=True).first(),
            menu=b.menu_items.all(),  # el menú es informativo; `available` se muestra tal cual
        )
        return Response(s.PublicBusinessSerializer(view).data)


class MyCardsView(APIView):
    @extend_schema(responses=s.CardSerializer(many=True))
    def get(self, request):
        cards = request.user.cards.select_related("business__program")
        return Response(s.CardSerializer([selectors.card_view(c) for c in cards], many=True).data)


class ActivateCardView(BusinessScoped, generics.GenericAPIView):
    serializer_class = s.CardSerializer

    @extend_schema(request=None, responses={200: s.CardSerializer, 409: s.ErrorSerializer})
    def post(self, request, slug):
        """El cliente activa su tarjeta (vacía) en un negocio con programa activo."""
        business = self.business
        if not m.Program.objects.filter(business=business, is_active=True).exists():
            return Response({"code": "no_active_program", "detail": "El negocio no tiene programa activo."}, status=409)
        card, _ = m.Card.objects.get_or_create(business=business, customer=request.user)
        return Response(s.CardSerializer(selectors.card_view(card)).data)


class ConsentView(BusinessScoped, generics.GenericAPIView):
    serializer_class = s.ConsentSerializer

    @extend_schema(responses=s.ConsentSerializer)
    def put(self, request, slug):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        m.Consent.objects.update_or_create(
            business=self.business, customer=request.user, channel="email",
            defaults={"granted": data.validated_data["granted"]},
        )
        return Response(data.validated_data)


# ---------- Personal ----------
class CustomerLookupView(BusinessScoped, APIView):
    permission_classes = [IsBusinessStaff]

    @extend_schema(
        parameters=[OpenApiParameter("q", str, required=True, description="Código del cliente (ej. OLI · 482 916) o correo")],
        responses={200: s.CustomerLookupSerializer, 404: s.ErrorSerializer},
    )
    def get(self, request, slug):
        business = self.business
        q = request.query_params.get("q", "").strip().lower()
        digits = "".join(ch for ch in q if ch.isdigit())
        if "@" in q:
            user = User.objects.filter(email=q, is_active=True).first()
        else:
            card = m.Card.objects.filter(business=business, code=digits, customer__is_active=True).first() if len(digits) == 6 else None
            user = card and card.customer
        program = m.Program.objects.filter(business=business).first()
        if user is None or program is None:
            return Response({"code": "unknown_customer", "detail": "No encontramos un cliente con ese código o correo."}, status=404)
        card = m.Card.objects.filter(business=business, customer=user).first()
        now = timezone.now()
        rewards = [
            r for r in m.Reward.objects.filter(business=business, customer=user, status=m.Reward.AVAILABLE)
            if r.expires_at > now
        ]
        body = {
            "email": user.email,
            "customer_code": card.display_code if card else None,
            "stamps": card.stamps if card else 0,
            "stamps_required": program.stamps_required,
            "rewards": rewards,
        }
        return Response(s.CustomerLookupSerializer(body).data)


def _purchase_qs(business):
    return m.Purchase.objects.filter(business=business).select_related(
        "customer", "registered_by", "reversal", "reward"
    )


class PurchaseCreateView(BusinessScoped, generics.GenericAPIView):
    permission_classes = [IsBusinessStaff]
    serializer_class = s.PurchaseInSerializer

    @extend_schema(responses={200: s.PurchaseResultSerializer, 201: s.PurchaseResultSerializer, **ERRORS})
    def post(self, request, slug):
        """Registra una compra ya pagada en caja. La `reference` es la clave de idempotencia."""
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        business = self.business
        result = container.register_purchase()(
            business.id, request.user.id, **data.validated_data
        )
        purchase = _purchase_qs(business).get(pk=result.purchase_id)
        program = business.program
        card = m.Card.objects.get(business=business, customer=purchase.customer)
        body = {"created": result.created, "stamps": card.stamps, "stamps_required": program.stamps_required, "purchase": purchase}
        return Response(s.PurchaseResultSerializer(body).data, status=201 if result.created else 200)


class RedeemView(BusinessScoped, APIView):
    permission_classes = [IsBusinessStaff]

    @extend_schema(request=None, responses={204: None, **ERRORS})
    def post(self, request, slug, reward_id):
        container.redeem_reward()(self.business.id, request.user.id, reward_id)
        return Response(status=204)


# ---------- Administración ----------
def _range(request):
    q = s.DateRangeSerializer(data=request.query_params)
    q.is_valid(raise_exception=True)
    today = timezone.localdate()
    return q.validated_data.get("start", today - timedelta(days=30)), q.validated_data.get("end", today), q.validated_data.get("type")


class SummaryView(BusinessScoped, APIView):
    permission_classes = [IsBusinessAdmin]

    @extend_schema(parameters=[s.DateRangeSerializer], responses=s.SummarySerializer)
    def get(self, request, slug):
        start, end, _ = _range(request)
        return Response(selectors.summary(self.business, start, end))


class ActivityView(BusinessScoped, APIView):
    permission_classes = [IsBusinessAdmin]

    @extend_schema(parameters=[s.DateRangeSerializer], responses=s.ActivitySerializer(many=True))
    def get(self, request, slug):
        start, end, kind = _range(request)
        return Response(s.ActivitySerializer(selectors.activity(self.business, start, end, kind), many=True).data)


class PurchaseDetailView(BusinessScoped, APIView):
    permission_classes = [IsBusinessAdmin]

    @extend_schema(responses={200: s.PurchaseSerializer, 404: s.ErrorSerializer})
    def get(self, request, slug, purchase_id):
        return Response(s.PurchaseSerializer(get_object_or_404(_purchase_qs(self.business), pk=purchase_id)).data)


class ReverseView(BusinessScoped, generics.GenericAPIView):
    permission_classes = [IsBusinessAdmin]
    serializer_class = s.ReverseSerializer

    @extend_schema(responses={204: None, **ERRORS})
    def post(self, request, slug, purchase_id):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        container.reverse_purchase()(self.business.id, request.user.id, purchase_id, data.validated_data["reason"])
        return Response(status=204)
