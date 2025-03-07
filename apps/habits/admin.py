from django.contrib import admin
from .models import Habit, Goal, HabitLog, Reminder


admin.site.register(Habit)
admin.site.register(Goal)
admin.site.register(HabitLog)
admin.site.register(Reminder)
