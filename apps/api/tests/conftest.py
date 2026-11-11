import pytest
from rest_framework.test import APIClient

from mesa.identity.adapters.mailers import ConsoleMailer
from mesa.identity.models import User
from mesa.loyalty import models as m


@pytest.fixture(autouse=True)
def clean_outbox():
    ConsoleMailer.sent.clear()


def make_business(slug="olivo", stamps_required=3):
    b = m.Business.objects.create(slug=slug, name=slug.title())
    m.Program.objects.create(business=b, reward_name="Americano", min_purchase_cop=12000, stamps_required=stamps_required)
    return b


def make_user(email, business=None, role=None):
    u = User.objects.create_user(email)
    if business:
        m.Membership.objects.create(business=business, user=u, role=role)
    return u


def client_for(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


@pytest.fixture
def olivo(db):
    return make_business("olivo")


@pytest.fixture
def staff(olivo):
    return client_for(make_user("staff@olivo.co", olivo, m.Membership.STAFF))


@pytest.fixture
def admin(olivo):
    return client_for(make_user("admin@olivo.co", olivo, m.Membership.ADMIN))


@pytest.fixture
def customer(db):
    return make_user("ana@example.com")


def buy(client, slug, email, ref, amount=15000):
    return client.post(f"/api/v1/b/{slug}/purchases", {"customer_email": email, "amount_cop": amount, "reference": ref}, format="json")
