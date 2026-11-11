import secrets

from django.conf import settings
from django.db import models


class Business(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="menu_items")
    category = models.CharField(max_length=60)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    price_cop = models.PositiveIntegerField()  # COP entero, sin decimales
    available = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category", "position", "name"]


class Program(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="program")
    reward_name = models.CharField(max_length=120)
    min_purchase_cop = models.PositiveIntegerField()
    stamps_required = models.PositiveSmallIntegerField()
    reward_valid_days = models.PositiveSmallIntegerField(default=30)
    conditions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


class Membership(models.Model):
    ADMIN, STAFF = "admin", "staff"
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=[(ADMIN, "Administrador"), (STAFF, "Atención")])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["business", "user"], name="uniq_membership")]


class Card(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="cards")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cards")
    stamps = models.PositiveSmallIntegerField(default=0)
    code = models.CharField(max_length=6, editable=False)  # código visible del cliente en este negocio

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["business", "customer"], name="uniq_card"),
            models.UniqueConstraint(fields=["business", "code"], name="uniq_card_code"),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            # shortcut: 10^6 códigos por negocio; ampliar longitud si un negocio supera ~100k tarjetas.
            while True:
                self.code = f"{secrets.randbelow(10**6):06d}"
                if not Card.objects.filter(business_id=self.business_id, code=self.code).exists():
                    break
        super().save(*args, **kwargs)

    @property
    def display_code(self) -> str:
        return f"{self.business.slug[:3].upper()} · {self.code[:3]} {self.code[3:]}"


class Purchase(models.Model):
    """Evento inmutable. Las correcciones se registran en PurchaseReversal."""

    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="purchases")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchases")
    amount_cop = models.PositiveIntegerField()
    reference = models.CharField(max_length=64)  # clave de idempotencia por negocio
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["business", "reference"], name="uniq_purchase_reference")]
        ordering = ["-created_at", "-id"]


class PurchaseReversal(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.PROTECT, related_name="reversal")
    reason = models.CharField(max_length=300)
    reversed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)


class Reward(models.Model):
    AVAILABLE, REDEEMED, VOIDED = "available", "redeemed", "voided"
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="rewards")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rewards")
    purchase = models.OneToOneField(Purchase, on_delete=models.PROTECT, related_name="reward")  # la compra que completó la tarjeta
    status = models.CharField(max_length=10, default=AVAILABLE)
    earned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        ordering = ["-earned_at", "-id"]


class Consent(models.Model):
    """Consentimiento comercial por negocio y canal; opcional y revocable."""

    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, default="email")
    granted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["business", "customer", "channel"], name="uniq_consent")]


class StampContribution(models.Model):
    """El sello de una compra y la recompensa exacta que financió, si ya se completó."""

    purchase = models.OneToOneField(Purchase, on_delete=models.PROTECT, related_name="stamp_contribution")
    reward = models.ForeignKey(Reward, null=True, blank=True, on_delete=models.PROTECT, related_name="contributions")
