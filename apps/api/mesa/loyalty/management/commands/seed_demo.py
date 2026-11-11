from django.core.management.base import BaseCommand

from mesa.identity.models import User
from mesa.loyalty import models as m


class Command(BaseCommand):
    help = "Crea el negocio sintético 'Café Olivo' con menú, programa y personal (solo demo/piloto local)."

    def handle(self, *args, **opts):
        b, _ = m.Business.objects.get_or_create(
            slug="cafe-olivo",
            defaults=dict(name="Café Olivo", description="Cafetería de barrio (datos sintéticos).", address="Calle 1 # 2-3"),
        )
        m.Program.objects.get_or_create(
            business=b,
            defaults=dict(reward_name="Americano mediano", min_purchase_cop=12000, stamps_required=10, reward_valid_days=30,
                          conditions="Un sello por compra pagada de COP 12.000 o más."),
        )
        if not b.menu_items.exists():
            m.MenuItem.objects.bulk_create(
                [m.MenuItem(business=b, category="Café", name=n, price_cop=p, description=d)
                 for n, p, d in [("Americano", 6000, "Mediano"), ("Capuchino", 9000, ""), ("Croissant", 7500, "De mantequilla")]]
            )
        for email, role in [("admin@cafe-olivo.test", m.Membership.ADMIN), ("barista@cafe-olivo.test", m.Membership.STAFF)]:
            user = User.objects.filter(email=email).first() or User.objects.create_user(email)
            m.Membership.objects.get_or_create(business=b, user=user, defaults={"role": role})
        self.stdout.write("Listo: /b/cafe-olivo — personal: admin@cafe-olivo.test, barista@cafe-olivo.test")
