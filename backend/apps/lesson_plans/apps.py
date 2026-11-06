from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LessonPlansConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lesson_plans"
    verbose_name = _("Lesson plans")
