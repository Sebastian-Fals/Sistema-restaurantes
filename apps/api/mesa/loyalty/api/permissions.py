from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from mesa.loyalty.models import Business, Membership


class _HasRole(BasePermission):
    roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        # 403 tanto si el negocio no existe como si no pertenece al usuario: no revela negocios ajenos.
        return (
            request.user.is_authenticated
            and Membership.objects.filter(
                business__slug=view.kwargs["slug"], user=request.user, role__in=self.roles
            ).exists()
        )


class IsBusinessStaff(_HasRole):
    roles = (Membership.ADMIN, Membership.STAFF)


class IsBusinessAdmin(_HasRole):
    roles = (Membership.ADMIN,)


class BusinessScoped:
    """Mixin: resuelve el negocio de la URL. Todas las consultas deben filtrar por él."""

    @property
    def business(self) -> Business:
        return get_object_or_404(Business, slug=self.kwargs["slug"], is_active=True)
