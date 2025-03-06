from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Goal, HabitLog


@shared_task
def reset_streaks_for_inactive_habits():
    now = timezone.now()

    goals_to_reset = Goal.objects.filter(status='in_progress').select_related('habit')

    for goal in goals_to_reset:
        habit = goal.habit

        if habit.frequency == 'daily':
            previous_day = (now - timedelta(days=1)).date()
            habit_logs = HabitLog.objects.filter(
                habit=habit,
                completed_at__date=previous_day
            )
            if not habit_logs.exists():
                goal.current_streak = 0
                goal.save()

        elif habit.frequency == 'monthly':
            previous_month = now.month - 1 if now.month > 1 else 12
            year = now.year if now.month > 1 else now.year - 1
            habit_logs = HabitLog.objects.filter(
                habit=habit,
                completed_at__year=year,
                completed_at__month=previous_month,
            )
            if not habit_logs.exists():
                goal.current_streak = 0
                goal.save()
