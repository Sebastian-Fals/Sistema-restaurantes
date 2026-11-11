from email.utils import parseaddr

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email


class Command(BaseCommand):
    help = "Comprueba la configuración de Resend sin enviar correo ni mostrar secretos."

    def handle(self, *args, **options):
        errors = []
        if settings.MAIL_ADAPTER != "resend":
            errors.append("MAIL_ADAPTER debe ser resend para entregar códigos por correo.")
        if not settings.RESEND_API_KEY.strip():
            errors.append("Falta RESEND_API_KEY.")
        _, sender = parseaddr(settings.RESEND_FROM)
        try:
            validate_email(sender)
        except ValidationError:
            errors.append("RESEND_FROM debe contener una dirección de correo válida.")
        else:
            domain = sender.rsplit("@", 1)[1].lower()
            if domain in {"example.com", "example.org", "example.net", "tu-dominio.co"} or domain.endswith((".example", ".test", ".invalid", ".local")):
                errors.append("RESEND_FROM todavía usa un dominio de ejemplo; configura tu dominio verificado.")
        if errors:
            raise CommandError(" ".join(errors))
        self.stdout.write(self.style.SUCCESS(
            "Configuración local de correo completa. No se enviaron mensajes; falta comprobar la entrega real y el dominio en Resend."
        ))
