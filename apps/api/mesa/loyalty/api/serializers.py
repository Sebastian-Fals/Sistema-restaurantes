from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from mesa.loyalty import models as m


class ErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    detail = serializers.CharField()


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.MenuItem
        fields = ["category", "name", "description", "price_cop", "available"]


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Program
        fields = ["reward_name", "min_purchase_cop", "stamps_required", "reward_valid_days", "conditions"]


class PublicBusinessSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    address = serializers.CharField(allow_blank=True)
    contact_email = serializers.CharField(allow_blank=True)
    contact_phone = serializers.CharField(allow_blank=True)
    program = ProgramSerializer(allow_null=True)
    menu = MenuItemSerializer(many=True)


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Reward
        fields = ["id", "status", "earned_at", "expires_at"]


class PurchaseSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.email")
    registered_by_email = serializers.EmailField(source="registered_by.email")
    reversed = serializers.SerializerMethodField()
    reversal_reason = serializers.SerializerMethodField()
    reward_id = serializers.SerializerMethodField()

    class Meta:
        model = m.Purchase
        fields = [
            "id", "customer_email", "amount_cop", "reference", "created_at",
            "registered_by_email", "reversed", "reversal_reason", "reward_id",
        ]

    def get_reversed(self, p) -> bool:
        return hasattr(p, "reversal")

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_reversal_reason(self, p):
        return p.reversal.reason if hasattr(p, "reversal") else None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_reward_id(self, p):
        return p.reward.id if hasattr(p, "reward") else None


class RecentPurchaseSerializer(serializers.ModelSerializer):
    reversed = serializers.SerializerMethodField()

    class Meta:
        model = m.Purchase
        fields = ["id", "amount_cop", "created_at", "reversed"]

    def get_reversed(self, p) -> bool:
        return hasattr(p, "reversal")


class CardSerializer(serializers.Serializer):
    customer_code = serializers.CharField()
    business_slug = serializers.CharField()
    business_name = serializers.CharField()
    reward_name = serializers.CharField()
    stamps = serializers.IntegerField()
    stamps_required = serializers.IntegerField()
    marketing_consent = serializers.BooleanField()
    rewards = RewardSerializer(many=True)
    recent_purchases = RecentPurchaseSerializer(many=True)


class ConsentSerializer(serializers.Serializer):
    granted = serializers.BooleanField()


class PurchaseInSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    amount_cop = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(max_length=64)


class PurchaseResultSerializer(serializers.Serializer):
    created = serializers.BooleanField()
    stamps = serializers.IntegerField()
    stamps_required = serializers.IntegerField()
    purchase = PurchaseSerializer()


class CustomerLookupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    customer_code = serializers.CharField(allow_null=True)
    stamps = serializers.IntegerField()
    stamps_required = serializers.IntegerField()
    rewards = RewardSerializer(many=True)


class ReverseSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=300)


class DateRangeSerializer(serializers.Serializer):
    start = serializers.DateField(required=False)
    end = serializers.DateField(required=False)
    type = serializers.ChoiceField(choices=["purchase", "reversal", "redemption"], required=False)


class DailyStampsSerializer(serializers.Serializer):
    date = serializers.DateField()
    stamps = serializers.IntegerField()


class SummarySerializer(serializers.Serializer):
    customers = serializers.IntegerField()
    purchases = serializers.IntegerField()
    stamps_credited = serializers.IntegerField()
    rewards_earned = serializers.IntegerField()
    rewards_redeemed = serializers.IntegerField()
    rewards_available = serializers.IntegerField()
    returning_customers = serializers.IntegerField(help_text="Clientes con 2+ compras en el periodo")
    daily = DailyStampsSerializer(many=True, help_text="Sellos por día, últimos 7 días hasta `end`")


class ActivitySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["purchase", "reversal", "redemption"])
    at = serializers.DateTimeField()
    actor_email = serializers.EmailField()
    customer_email = serializers.EmailField()
    amount_cop = serializers.IntegerField(allow_null=True)
    detail = serializers.CharField(allow_blank=True)
    purchase_id = serializers.IntegerField()


class MembershipSerializer(serializers.Serializer):
    business_slug = serializers.CharField()
    role = serializers.ChoiceField(choices=["admin", "staff"])


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    memberships = MembershipSerializer(many=True)
