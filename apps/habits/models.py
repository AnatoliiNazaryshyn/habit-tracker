from django.db import models
from django.contrib.auth import get_user_model
from .constants import FREQUENCY_CHOICES, GOAL_STATUS_CHOICES


User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit.name} completed at {self.completed_at}"


class Goal(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='goals')
    status = models.CharField(max_length=11, choices=GOAL_STATUS_CHOICES, default='in_progress')
    current_streak = models.PositiveIntegerField(default=0)
    target_streak = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.habit.name} - Goal: {self.current_streak} out of {self.target_streak}"


class Reminder(models.Model):
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='reminder')
    reminder_time = models.TimeField()

    def __str__(self):
        return f"Reminder on {self.habit.name} at {self.reminder_time}"
