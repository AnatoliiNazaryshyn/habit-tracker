from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from .models import Goal, HabitLog, Reminder


sg_client = SendGridAPIClient(settings.SENDGRID_API_KEY)


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


@shared_task
def send_daily_reminders():
    current_time = timezone.now().time()

    reminders = Reminder.objects.filter(
        reminder_time__hour=current_time.hour,
        reminder_time__minute=current_time.minute
    ).select_related('habit__user')

    for reminder in reminders:
        send_reminder_email.delay(
            user_email=reminder.habit.user.email,
            habit_name=reminder.habit.name
        )

    return f"Queued {reminders.count()} reminder emails"


@shared_task(rate_limit='100/m', bind=True, max_retries=3)
def send_reminder_email(self, user_email, habit_name):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=user_email,
        subject=f"Reminder: Time for your habit - {habit_name}",
        html_content=f"""
            <h2>Habit Reminder</h2>
            <p>Hi,</p>
            <p>This is a reminder to complete your habit: <strong>{habit_name}</strong></p>
            <p>Keep up the good work!</p>
        """
    )

    try:
        response = sg_client.send(message)
        return f"Reminder sent to {user_email} - Status: {response.status_code}"
    except Exception as e:
        retry_in = 5 * (2 ** self.request.retries)
        self.retry(exc=e, countdown=retry_in)
