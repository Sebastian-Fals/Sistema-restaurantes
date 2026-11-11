from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import path

from mesa import container
from mesa.identity.models import User


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifySerializer(EmailSerializer):
    code = serializers.CharField(max_length=10)


class CsrfView(APIView):
    """Entrega la cookie CSRF; el frontend la reenvía en X-CSRFToken."""

    permission_classes = [AllowAny]

    @extend_schema(responses={204: None})
    def get(self, request):
        get_token(request)
        return Response(status=204)


class RequestCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailSerializer

    @extend_schema(responses={204: None})
    def post(self, request):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        container.request_login_code()(data.validated_data["email"])
        return Response(status=204)


class VerifyCodeView(generics.GenericAPIView):
    """Registro e inicio de sesión son el mismo flujo: crea la cuenta si no existe."""

    permission_classes = [AllowAny]
    serializer_class = VerifySerializer

    @extend_schema(responses={204: None})
    def post(self, request):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        user_id = container.verify_login_code()(data.validated_data["email"], data.validated_data["code"])
        login(request, User.objects.get(pk=user_id), backend="django.contrib.auth.backends.ModelBackend")
        return Response(status=204)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        logout(request)
        return Response(status=204)


urlpatterns = [
    path("auth/csrf", CsrfView.as_view()),
    path("auth/code", RequestCodeView.as_view()),
    path("auth/verify", VerifyCodeView.as_view()),
    path("auth/logout", LogoutView.as_view()),
]
