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

        last_log = HabitLog.objects.filter(habit=habit).order_by('-completed_at').first()

        if last_log:
            now = timezone.now()
            last_log_time = last_log.completed_at

            if habit.frequency == 'daily':
                if last_log_time.date() == now.date():
                    raise serializers.ValidationError({
                        'habit': 'You can only log daily habit once per day.'
                    })

            elif habit.frequency == 'monthly':
                if (last_log_time.year == now.year and last_log_time.month == now.month):
                    raise serializers.ValidationError({
                        'habit': 'You can only log monthly habit once per month.'
                    })

        return data
