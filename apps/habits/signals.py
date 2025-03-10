from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HabitLog, Goal


@receiver(post_save, sender=HabitLog)
def update_goal_current_streak(sender, instance, created, **kwargs):
    if created:
        habit = instance.habit
        goal = Goal.objects.filter(habit=habit, status='in_progress').first()

        if goal:
            goal.current_streak += 1

            if goal.current_streak >= goal.target_streak:
                goal.status = 'completed'

            goal.save()
