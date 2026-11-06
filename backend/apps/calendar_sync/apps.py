from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CalendarSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.calendar_sync"
    verbose_name = _("Calendar Sync")
