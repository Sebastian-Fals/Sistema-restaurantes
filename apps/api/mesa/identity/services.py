"""Identity cleanup used when an account is anonymized."""

from django.contrib.sessions.models import Session
from django.db import transaction

from .models import LoginCode, User


@transaction.atomic
def remove_account_access(customer_id: int) -> None:
    """Remove login challenges and every database session before losing the email.

    The caller anonymizes User in the same transaction. Loyalty events retain
    their protected foreign keys; no purchase, card or reward is deleted here.
    """
    user = User.objects.select_for_update().get(pk=customer_id)
    LoginCode.objects.filter(email__iexact=user.email).delete()
    # Session payloads are signed rather than queryable JSON. Pilot volumes are
    # small; stream them instead of loading the whole session table in memory.
    keys = []
    for session in Session.objects.iterator(chunk_size=500):
        if str(session.get_decoded().get("_auth_user_id")) == str(customer_id):
            keys.append(session.session_key)
        if len(keys) >= 500:
            Session.objects.filter(session_key__in=keys).delete()
            keys.clear()
    if keys:
        Session.objects.filter(session_key__in=keys).delete()
