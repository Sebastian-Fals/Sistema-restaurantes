from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from mesa.identity.api import urlpatterns as identity_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(identity_urls)),
    path("api/v1/", include("mesa.loyalty.api.urls")),
    path("api/v1/schema", SpectacularAPIView.as_view(), name="schema"),
]
