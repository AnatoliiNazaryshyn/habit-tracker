from rest_framework import viewsets, generics
from .models import Habit, Goal, HabitLog
from .serializers import HabitSerializer, GoalSerializer, HabitLogSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer

    def get_queryset(self):
        user = self.request.user
        return Goal.objects.filter(habit__user=user)


class HabitLogListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitLogSerializer

    def get_queryset(self):
        user = self.request.user
        return HabitLog.objects.filter(habit__user=user)
