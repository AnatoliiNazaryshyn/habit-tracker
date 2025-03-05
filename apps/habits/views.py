from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Habit, Goal, HabitLog
from .serializers import (
    HabitSerializer, GoalSerializer,
    HabitLogSerializer, HabitDashboardSerializer
)


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing habits.

    Provides CRUD operations for habits and includes a dashboard endpoint.
    Only displays and allows operations on habits owned by the current user.
    """
    serializer_class = HabitSerializer

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Return a dashboard view of all user habits with current goals and logs.

        For each habit, includes:
        - Basic habit information
        - Current in-progress goal (if exists)
        - Today's log for daily habits or this month's log for monthly habits
        """
        habits = self.get_queryset()
        serializer = HabitDashboardSerializer(habits, many=True)
        return Response(serializer.data)


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing habit goals.

    Provides CRUD operations for goals and enforces business rules:
    - Only one 'in_progress' goal allowed per habit
    - Users can only create goals for habits they own
    """
    serializer_class = GoalSerializer

    def get_queryset(self):
        user = self.request.user
        return Goal.objects.filter(habit__user=user)


class HabitLogListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating habit logs.

    Provide Create, Read operations and enforces business rules:
    - Users can only log their own habits
    - Daily habits can only be logged once per day
    - Monthly habits can only be logged once per month
    """
    serializer_class = HabitLogSerializer

    def get_queryset(self):
        user = self.request.user
        return HabitLog.objects.filter(habit__user=user)
