"""Raíz de composición: único lugar que une casos de uso con sus adaptadores concretos."""

from django.conf import settings

from mesa.identity.adapters.mailers import make_mailer
from mesa.identity.adapters.orm import DjangoLoginCodeStore, DjangoUserDirectory
from mesa.identity.use_cases import RequestLoginCode, VerifyLoginCode
from mesa.loyalty.adapters.orm import DjangoLoyaltyRepository
from mesa.loyalty.use_cases import (
    ActivateCard,
    DeleteAccount,
    LookupCustomer,
    RedeemReward,
    RegisterPurchase,
    ReversePurchase,
    SetConsent,
)


def request_login_code() -> RequestLoginCode:
    return RequestLoginCode(DjangoLoginCodeStore(), make_mailer(), settings.SECRET_KEY)


def verify_login_code() -> VerifyLoginCode:
    return VerifyLoginCode(DjangoLoginCodeStore(), DjangoUserDirectory(), settings.SECRET_KEY)


def register_purchase() -> RegisterPurchase:
    return RegisterPurchase(DjangoLoyaltyRepository())


def redeem_reward() -> RedeemReward:
    return RedeemReward(DjangoLoyaltyRepository())


def reverse_purchase() -> ReversePurchase:
    return ReversePurchase(DjangoLoyaltyRepository())


def activate_card() -> ActivateCard:
    return ActivateCard(DjangoLoyaltyRepository())


def lookup_customer() -> LookupCustomer:
    return LookupCustomer(DjangoLoyaltyRepository())


def set_consent() -> SetConsent:
    return SetConsent(DjangoLoyaltyRepository())


def delete_account() -> DeleteAccount:
    return DeleteAccount(DjangoLoyaltyRepository())
