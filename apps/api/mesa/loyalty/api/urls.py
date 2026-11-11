from django.urls import path

from . import views as v

urlpatterns = [
    path("me", v.MeView.as_view()),
    path("me/cards", v.MyCardsView.as_view()),
    path("public/b/<slug:slug>", v.PublicBusinessView.as_view()),
    path("b/<slug:slug>/card", v.ActivateCardView.as_view()),
    path("b/<slug:slug>/consent", v.ConsentView.as_view()),
    path("b/<slug:slug>/customer", v.CustomerLookupView.as_view()),
    path("b/<slug:slug>/purchases", v.PurchaseCreateView.as_view()),
    path("b/<slug:slug>/purchases/<int:purchase_id>", v.PurchaseDetailView.as_view()),
    path("b/<slug:slug>/purchases/<int:purchase_id>/reverse", v.ReverseView.as_view()),
    path("b/<slug:slug>/rewards/<int:reward_id>/redeem", v.RedeemView.as_view()),
    path("b/<slug:slug>/summary", v.SummaryView.as_view()),
    path("b/<slug:slug>/activity", v.ActivityView.as_view()),
]
