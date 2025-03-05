from django.apps import AppConfig


class HabitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.habits"

    def ready(self):
        import apps.habits.signals  # noqa: F401
