from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeetingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.meeting"
    verbose_name = _("Video meetings")
