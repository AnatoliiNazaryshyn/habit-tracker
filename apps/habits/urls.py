from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, GoalViewSet, HabitLogListCreateView, ReminderViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'reminders', ReminderViewSet, basename='reminder')

app_name = 'habits'

urlpatterns = [
    path('', include(router.urls)),
    path('habit-logs/', HabitLogListCreateView.as_view(), name='habit-log-list-create'),
]
