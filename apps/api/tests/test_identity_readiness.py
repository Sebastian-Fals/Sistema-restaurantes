from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from mesa.identity.adapters.mailers import ConsoleMailer, ResendMailer, make_mailer
from mesa.identity.adapters.orm import DjangoLoginCodeStore
from mesa.identity.domain import hash_code
from mesa.identity.models import LoginCode, User
from mesa.loyalty.models import Card, Consent, Membership, Purchase

from .conftest import buy, client_for, make_business, make_user

pytestmark = pytest.mark.django_db


def issue(email, code="123456", *, age=0, used=False):
    now = timezone.now()
    return LoginCode.objects.create(
        email=email, code_hash=hash_code(email, code, settings.SECRET_KEY),
        created_at=now - timedelta(seconds=age), expires_at=now + timedelta(minutes=10), used=used,
    )


def test_only_latest_code_issuance_can_be_used_even_after_it_is_consumed():
    email = "ana@example.com"
    old = issue(email, "111111", age=61)
    latest = issue(email, "222222")
    client = APIClient()
    assert client.post("/api/v1/auth/verify", {"email": email, "code": "111111"}, format="json").status_code == 400
    assert client.post("/api/v1/auth/verify", {"email": email, "code": "222222"}, format="json").status_code == 204
    # An old unconsumed row from existing data must not become usable again.
    assert LoginCode.objects.get(pk=old.pk).used is False
    assert LoginCode.objects.get(pk=latest.pk).used is True
    assert APIClient().post("/api/v1/auth/verify", {"email": email, "code": "111111"}, format="json").status_code == 400


def test_resending_invalidates_previous_pending_codes():
    email = "ana@example.com"
    old = issue(email, age=61)
    assert APIClient().post("/api/v1/auth/code", {"email": email}, format="json").status_code == 204
    old.refresh_from_db()
    assert old.used is True
    assert LoginCode.objects.filter(email=email, used=False).count() == 1


def test_disabled_account_cannot_complete_login():
    email = "disabled@example.com"
    user = User.objects.create_user(email)
    user.is_active = False
    user.save()
    issue(email)
    client = APIClient()
    assert client.post("/api/v1/auth/verify", {"email": email, "code": "123456"}, format="json").status_code == 400
    assert client.get("/api/v1/me").status_code in (401, 403)


def test_deleting_account_revokes_all_sessions_and_codes_but_preserves_loyalty_history():
    business = make_business("privacy")
    user = make_user("ana@example.com")
    staff = make_user("staff@example.com", business, Membership.STAFF)
    purchase = buy(client_for(staff), business.slug, user.email, "PRIVACY-1")
    assert purchase.status_code == 201
    Consent.objects.create(business=business, customer=user, granted=True)
    challenge = issue(user.email)
    first, second, other = APIClient(), APIClient(), APIClient()
    for client, account in [(first, user), (second, user), (other, staff)]:
        client.force_login(account, backend="django.contrib.auth.backends.ModelBackend")
    first_session = first.cookies[settings.SESSION_COOKIE_NAME].value
    second_session = second.cookies[settings.SESSION_COOKIE_NAME].value
    other_session = other.cookies[settings.SESSION_COOKIE_NAME].value

    assert first.delete("/api/v1/me").status_code == 204
    assert not Session.objects.filter(session_key__in=[first_session, second_session]).exists()
    assert Session.objects.filter(session_key=other_session).exists()
    assert not LoginCode.objects.filter(pk=challenge.pk).exists()
    assert not Consent.objects.filter(customer=user).exists()
    assert Purchase.objects.filter(customer_id=user.pk).count() == 1
    assert Card.objects.filter(customer_id=user.pk).count() == 1
    for client in [first, second]:
        assert client.get("/api/v1/me").status_code in (401, 403)
    assert other.get("/api/v1/me").status_code == 200

    original_email = user.email
    user.refresh_from_db()
    assert user.email != original_email and user.is_active is False
    # A fresh signup with the same email must not inherit the deleted account's history.
    fresh = APIClient()
    assert fresh.post("/api/v1/auth/code", {"email": original_email}, format="json").status_code == 204
    _, code = ConsoleMailer.sent[-1]
    assert fresh.post("/api/v1/auth/verify", {"email": original_email, "code": code}, format="json").status_code == 204
    assert fresh.get("/api/v1/me").json()["id"] != user.pk
    assert fresh.get("/api/v1/me/cards").json() == []


def test_purge_removes_expired_codes_without_resetting_live_cooldown_or_exposing_data():
    now = timezone.now()
    expired = issue("expired@example.com", age=700)
    LoginCode.objects.filter(pk=expired.pk).update(expires_at=now - timedelta(seconds=1))
    used = issue("used@example.com", used=True)
    pending = issue("pending@example.com")
    output = StringIO()
    call_command("purge_login_codes", stdout=output)
    assert not LoginCode.objects.filter(pk=expired.pk).exists()
    assert set(LoginCode.objects.values_list("pk", flat=True)) == {used.pk, pending.pk}
    assert "@" not in output.getvalue() and "123456" not in output.getvalue()
    assert DjangoLoginCodeStore().last_created_at(used.email) == used.created_at
    assert APIClient().post("/api/v1/auth/code", {"email": used.email}, format="json").status_code == 429


@override_settings(MAIL_ADAPTER="console", RESEND_API_KEY="", RESEND_FROM="Mesa <no-reply@example.com>")
def test_mail_check_rejects_demo_configuration_without_printing_secrets():
    with pytest.raises(CommandError) as exc:
        call_command("check_mail_configuration")
    assert "MAIL_ADAPTER" in str(exc.value) and "RESEND_API_KEY" in str(exc.value)


@override_settings(MAIL_ADAPTER="resend", RESEND_API_KEY="private-test-key", RESEND_FROM="Mesa <acceso@cafeteria.co>")
def test_mail_check_is_read_only_and_resend_adapter_uses_configured_sender():
    output = StringIO()
    with patch("resend.Emails.send", return_value={"id": "test-only"}) as send:
        call_command("check_mail_configuration", stdout=output)
        send.assert_not_called()
        ResendMailer().send_login_code("ana@example.com", "123456")
        payload = send.call_args.args[0]
        assert payload["from"] == settings.RESEND_FROM
        assert payload["to"] == ["ana@example.com"]
        assert "123456" in payload["text"]
    assert "private-test-key" not in output.getvalue()


@pytest.mark.parametrize("adapter,key", [("resned", "private-test-key"), ("resend", "")])
def test_invalid_mail_configuration_cannot_silently_fall_back_to_console(adapter, key):
    with override_settings(MAIL_ADAPTER=adapter, RESEND_API_KEY=key):
        with pytest.raises(ImproperlyConfigured):
            make_mailer()
    assert ConsoleMailer.sent == []
