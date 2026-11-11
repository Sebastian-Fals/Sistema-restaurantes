from django.contrib import admin

from .models import User

admin.site.register(User, list_display=("email", "is_staff", "is_active"), search_fields=("email",))
