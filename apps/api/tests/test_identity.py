from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from mesa.identity.adapters.mailers import ConsoleMailer
from mesa.identity.models import LoginCode, User


def request_code(c, email="ana@example.com"):
    return c.post("/api/v1/auth/code", {"email": email}, format="json")


@pytest.mark.django_db
def test_signup_and_login_with_code():
    c = APIClient()
    assert request_code(c).status_code == 204
    email, code = ConsoleMailer.sent[-1]
    assert email == "ana@example.com"
    assert c.post("/api/v1/auth/verify", {"email": email, "code": code}, format="json").status_code == 204
    assert c.get("/api/v1/me").json()["email"] == "ana@example.com"
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_code_is_single_use_and_cooldown_applies():
    c = APIClient()
    request_code(c)
    assert request_code(c).status_code == 429  # cooldown de 60 s
    _, code = ConsoleMailer.sent[-1]
    body = {"email": "ana@example.com", "code": code}
    assert c.post("/api/v1/auth/verify", body, format="json").status_code == 204
    assert APIClient().post("/api/v1/auth/verify", body, format="json").status_code == 400


@pytest.mark.django_db
def test_wrong_code_locks_after_five_attempts():
    c = APIClient()
    request_code(c)
    _, code = ConsoleMailer.sent[-1]
    for _ in range(5):
        assert c.post("/api/v1/auth/verify", {"email": "ana@example.com", "code": "000000"}, format="json").status_code == 400
    assert c.post("/api/v1/auth/verify", {"email": "ana@example.com", "code": code}, format="json").status_code == 400


@pytest.mark.django_db
def test_expired_code_rejected():
    c = APIClient()
    request_code(c)
    _, code = ConsoleMailer.sent[-1]
    LoginCode.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    assert c.post("/api/v1/auth/verify", {"email": "ana@example.com", "code": code}, format="json").status_code == 400


@pytest.mark.django_db
def test_endpoints_require_login():
    assert APIClient().get("/api/v1/me").status_code in (401, 403)
