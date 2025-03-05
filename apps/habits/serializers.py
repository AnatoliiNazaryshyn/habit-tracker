from django.utils import timezone
from rest_framework import serializers
from .models import Habit, Goal, HabitLog


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'user', 'name', 'frequency', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'habit', 'current_streak', 'status', 'target_streak']
        read_only_fields = ['id', 'current_streak']

    def validate(self, data):
        habit = data.get('habit')
        user = self.context['request'].user

        if not habit:
            habit = self.instance.habit

        if habit.user != user:
            raise serializers.ValidationError({
                'habit': 'You can only create goals for your own habits.'
            })

        existing_goal = Goal.objects.filter(
            habit=data.get('habit'),
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
        user = self.context['request'].user

        if habit.user != user:
            raise serializers.ValidationError({
                'habit': 'You can only create logs for your own habits.'
            })

        now = timezone.now()

        if habit.frequency == 'daily':
            if HabitLog.objects.filter(
                habit=habit,
                completed_at__date=now.date()
            ).exists():
                raise serializers.ValidationError({
                    'habit': 'You can only log daily habit once per day.'
                })

        elif habit.frequency == 'monthly':
            if HabitLog.objects.filter(
                habit=habit,
                completed_at__year=now.year,
                completed_at__month=now.month
            ).exists():
                raise serializers.ValidationError({
                    'habit': 'You can only log monthly habit once per month.'
                })

        return data


class GoalCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'current_streak', 'status', 'target_streak']


class HabitLogCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'completed_at']


class HabitDashboardSerializer(serializers.ModelSerializer):
    current_goal = serializers.SerializerMethodField()
    today_log = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = ['id', 'name', 'frequency', 'current_goal', 'today_log']

    def get_current_goal(self, habit):
        goal = Goal.objects.filter(habit=habit, status='in_progress').first()
        return GoalCompactSerializer(goal).data if goal else None

    def get_today_log(self, habit):
        now = timezone.now()

        if habit.frequency == 'daily':
            log = habit.logs.filter(completed_at__date=now.date()).first()
            return HabitLogCompactSerializer(log).data if log else None

        elif habit.frequency == 'monthly':
            log = habit.logs.filter(
                completed_at__year=now.year,
                completed_at__month=now.month
            ).first()
            return HabitLogCompactSerializer(log).data if log else None

        return None
