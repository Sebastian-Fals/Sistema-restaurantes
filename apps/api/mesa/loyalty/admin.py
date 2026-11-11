"""Herramientas internas: el equipo Mesa configura negocios, menú, programa y personal desde aquí."""

from django.contrib import admin

from . import models as m


class MenuInline(admin.TabularInline):
    model = m.MenuItem
    extra = 0


class ProgramInline(admin.StackedInline):
    model = m.Program


class MembershipInline(admin.TabularInline):
    model = m.Membership
    extra = 0


@admin.register(m.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProgramInline, MenuInline, MembershipInline]


class ReadOnly(admin.ModelAdmin):
    """Eventos auditables: solo lectura."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register([m.Purchase, m.PurchaseReversal, m.Reward], ReadOnly)
