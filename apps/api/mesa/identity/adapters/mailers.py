import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

log = logging.getLogger(__name__)


class ConsoleMailer:
    """Desarrollo y tests: guarda los mensajes en `sent` (como el backend locmem de Django)."""

    sent: list[tuple[str, str]] = []

    def send_login_code(self, email, code):
        self.sent.append((email, code))
        log.warning("Código de acceso para %s: %s", email, code)


class ResendMailer:
    def send_login_code(self, email, code):
        import resend

        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": settings.RESEND_FROM,
                "to": [email],
                "subject": "Tu código de acceso",
                "text": f"Tu código de acceso es {code}. Vence en 10 minutos.",
            }
        )


def make_mailer():
    if settings.MAIL_ADAPTER == "console":
        return ConsoleMailer()
    if settings.MAIL_ADAPTER == "resend":
        if not settings.RESEND_API_KEY.strip():
            raise ImproperlyConfigured("MAIL_ADAPTER=resend necesita RESEND_API_KEY.")
        return ResendMailer()
    raise ImproperlyConfigured("MAIL_ADAPTER debe ser console o resend.")
