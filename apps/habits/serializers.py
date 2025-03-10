from django.utils import timezone
from rest_framework import serializers
from .models import Habit, Goal, HabitLog, Reminder


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'frequency', 'created_at']
        read_only_fields = ['id', 'created_at']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'habit', 'current_streak', 'status', 'target_streak']
        read_only_fields = ['id', 'current_streak']

    def validate(self, data):
        habit = data.get('habit')

        if habit and self.context.get('request') and self.context['request'].user != habit.user:
            raise serializers.ValidationError({
                'habit': 'You can only create goals for your own habits.'
            })

        if not habit and self.instance:
            habit = self.instance.habit

        if habit and (not self.instance or self.instance.status != 'in_progress'):
            existing_goal = Goal.objects.filter(
                habit=habit,
                status='in_progress'
            ).exists()

            if existing_goal:
                raise serializers.ValidationError({
                    'habit': 'An in-progress goal already exists for this habit.'
                })

        return data


class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'completed_at']
        read_only_fields = ['id', 'completed_at']

    def validate(self, data):
        habit = data.get('habit')

        if habit and self.context.get('request') and self.context['request'].user != habit.user:
            raise serializers.ValidationError({
                'habit': 'You can only logs your own habits.'
            })

        if habit:
            now = timezone.now()

            frequency_validators = {
                'daily': {
                    'filter': {'habit': habit, 'completed_at__date': now.date()},
                    'message': 'You can only log daily habit once per day.'
                },
                'monthly': {
                    'filter': {
                        'habit': habit,
                        'completed_at__year': now.year,
                        'completed_at__month': now.month
                    },
                    'message': 'You can only log monthly habit once per month.'
                }
            }

            validator = frequency_validators.get(habit.frequency)
            if validator and HabitLog.objects.filter(**validator['filter']).exists():
                raise serializers.ValidationError({'habit': validator['message']})

        return data


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'habit', 'reminder_time']
        read_only_fields = ['id']

    def validate_habit(self, value):
        if self.context.get('request') and self.context['request'].user != value.user:
            raise serializers.ValidationError('You can only create reminders for your own habits.')
        return value


class GoalCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'current_streak', 'status', 'target_streak']


class HabitLogCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'completed_at']


class ReminderCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'reminder_time']


class HabitDashboardSerializer(serializers.ModelSerializer):
    current_goal = serializers.SerializerMethodField()
    today_log = serializers.SerializerMethodField()
    reminder = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = ['id', 'name', 'frequency', 'current_goal', 'today_log', 'reminder']

    def get_current_goal(self, habit):
        goal = Goal.objects.filter(habit=habit, status='in_progress').first()
        return GoalCompactSerializer(goal).data if goal else None

    def get_today_log(self, habit):
        now = timezone.now()

        frequency_log_filters = {
            'daily': {'completed_at__date': now.date()},
            'monthly': {
                'completed_at__year': now.year,
                'completed_at__month': now.month
            }
        }

        log_filter = frequency_log_filters.get(habit.frequency, {})
        log = habit.logs.filter(**log_filter).first() if log_filter else None

        return HabitLogCompactSerializer(log).data if log else None

    def get_reminder(self, habit):
        reminder = getattr(habit, 'reminder', None)
        return ReminderCompactSerializer(reminder).data if reminder else None
