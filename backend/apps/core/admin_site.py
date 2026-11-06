"""Owner-only administration, separate from public demonstration accounts."""

from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class OwnerAdminSite(AdminSite):
    site_header = "Administracja upclass"
    site_title = "upclass — administracja"
    index_title = "Zarządzanie aplikacją"

    def has_permission(self, request):
        return (
            super().has_permission(request)
            and request.user.is_superuser
            and request.user.username not in {"demo_user", "demo_premium"}
        )


class OwnerAdminConfig(AdminConfig):
    default_site = "apps.core.admin_site.OwnerAdminSite"
