from datetime import timedelta

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from mesa import container
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
        container.delete_account()(request.user.id)
        return Response(status=204)


class PublicBusinessView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: s.PublicBusinessSerializer, 404: s.ErrorSerializer})
    def get(self, request, slug):
        view = selectors.public_business(slug)
        if view is None:
            raise Http404
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
        card = container.activate_card()(self.business.id, request.user.id)
        return Response(s.CardSerializer(selectors.card_view_by_id(card.id)).data)


class ConsentView(BusinessScoped, generics.GenericAPIView):
    serializer_class = s.ConsentSerializer

    @extend_schema(responses=s.ConsentSerializer)
    def put(self, request, slug):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        container.set_consent()(self.business.id, request.user.id, data.validated_data["granted"])
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
        customer_id = container.lookup_customer()(business.id, request.query_params.get("q", ""))
        return Response(s.CustomerLookupSerializer(selectors.customer_profile(business, customer_id)).data)


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
