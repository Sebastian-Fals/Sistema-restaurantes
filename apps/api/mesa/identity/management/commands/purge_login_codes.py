from django.core.management.base import BaseCommand
from django.utils import timezone

from mesa.identity.models import LoginCode


class Command(BaseCommand):
    help = "Elimina códigos de acceso vencidos, incluidos los ya usados, sin mostrar correos ni códigos."

    def handle(self, *args, **options):
        # Retain even consumed codes until their TTL: their timestamp enforces
        # resend cooldown and their position prevents older-code fallback.
        deleted, _ = LoginCode.objects.filter(expires_at__lte=timezone.now()).delete()
        self.stdout.write(f"Códigos de acceso vencidos eliminados: {deleted}.")
