from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Habit, Goal, HabitLog
from .serializers import (
    HabitSerializer, GoalSerializer,
    HabitLogSerializer, HabitDashboardSerializer
)


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        habits = self.get_queryset()
        serializer = HabitDashboardSerializer(habits, many=True)
        return Response(serializer.data)


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
