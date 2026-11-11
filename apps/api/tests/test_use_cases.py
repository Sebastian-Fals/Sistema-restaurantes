"""Casos de uso con dobles de los puertos: sin base de datos."""

from contextlib import nullcontext

import pytest

from mesa.loyalty import domain as d
from mesa.loyalty.use_cases import ActivateCard, LookupCustomer

RULES = d.Rules(min_purchase_cop=12000, stamps_required=3, reward_valid_days=30)


class FakeRepo:
    """Implementa solo los métodos de LoyaltyRepository que usan estos casos de uso."""

    def __init__(self, program=d.ProgramState(RULES, True), emails=None, codes=None):
        self._program, self.emails, self.codes, self.cards = program, emails or {}, codes or {}, {}

    def atomic(self):
        return nullcontext()

    def program(self, business_id):
        return self._program

    def customer_id_by_email(self, email):
        return self.emails.get(email)

    def customer_id_by_card_code(self, business_id, code):
        return self.codes.get((business_id, code))

    def get_or_create_card(self, business_id, customer_id):
        key = (business_id, customer_id)
        self.cards.setdefault(key, d.CardState(len(self.cards) + 1, 0))
        return self.cards[key]


def test_activate_card_is_idempotent():
    repo = FakeRepo()
    first = ActivateCard(repo)(1, 7)
    assert first == ActivateCard(repo)(1, 7) and first.stamps == 0 and len(repo.cards) == 1


@pytest.mark.parametrize("program", [None, d.ProgramState(RULES, False)])
def test_activate_card_requires_active_program(program):
    repo = FakeRepo(program=program)
    with pytest.raises(d.NoActiveProgram):
        ActivateCard(repo)(1, 7)
    assert repo.cards == {}


@pytest.mark.parametrize(
    "query, expected",
    [("OLI · 482 916", 7), ("482916", 7), ("  Ana@Example.com ", 8)],
)
def test_lookup_by_code_or_email(query, expected):
    repo = FakeRepo(emails={"ana@example.com": 8}, codes={(1, "482916"): 7})
    assert LookupCustomer(repo)(1, query) == expected


@pytest.mark.parametrize("query", ["", "48291", "OLI · 482 916", "nadie@example.com"])
def test_lookup_unknown_customer(query):
    repo = FakeRepo(codes={(2, "482916"): 7})  # el código existe, pero en otro negocio
    with pytest.raises(d.UnknownCustomer):
        LookupCustomer(repo)(1, query)


def test_lookup_without_program_is_unknown():
    with pytest.raises(d.UnknownCustomer):
        LookupCustomer(FakeRepo(program=None, emails={"ana@example.com": 8}))(1, "ana@example.com")
