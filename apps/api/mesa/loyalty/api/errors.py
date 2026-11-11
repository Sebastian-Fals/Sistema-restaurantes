from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler

from mesa.errors import DomainError

STATUS_BY_CODE = {
    "invalid_code": 400,
    "too_many_requests": 429,
    "unknown_customer": 404,
    "reward_not_found": 404,
    "purchase_not_found": 404,
    "below_minimum": 422,
}  # el resto de errores de dominio son conflictos de estado (409)


def exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response({"code": exc.code, "detail": str(exc)}, status=STATUS_BY_CODE.get(exc.code, 409))
    return drf_handler(exc, context)
