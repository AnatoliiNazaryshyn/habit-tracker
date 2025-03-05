import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.habits.models import Habit, Goal, HabitLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user_email():
    return 'test_user@example.com'


@pytest.fixture
def test_user_password():
    return 'test_password12345'


@pytest.fixture
def test_user(test_user_email, test_user_password):
    User = get_user_model()
    return User.objects.create_user(
        email=test_user_email,
        password=test_user_password
    )


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def habit_url():
    return reverse('habits:habit-list')


@pytest.fixture
def goal_url():
    return reverse('habits:goal-list')


@pytest.fixture
def habit_log_url():
    return reverse('habits:habit-log-list-create')


@pytest.fixture
def test_habit(test_user):
    return Habit.objects.create(
        user=test_user,
        name='Test Habit',
        frequency='daily'
    )


@pytest.fixture
def test_goal(test_habit):
    return Goal.objects.create(
        habit=test_habit,
        target_streak=10
    )


@pytest.fixture
def test_habit_log(test_habit):
    return HabitLog.objects.create(
        habit=test_habit
    )


@pytest.mark.django_db
class TestHabitAPI:
    def test_create_habit(self, authenticated_api_client, habit_url):
        data = {
            'name': 'New Habit',
            'frequency': 'daily'
        }
        response = authenticated_api_client.post(habit_url, data)

        assert response.status_code == 201
        assert Habit.objects.filter(name='New Habit').exists()

    def test_list_habits(self, authenticated_api_client, habit_url, test_habit):
        response = authenticated_api_client.get(habit_url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['name'] == test_habit.name

    def test_retrieve_habit(self, authenticated_api_client, test_habit):
        url = reverse('habits:habit-detail', args=[test_habit.id])
        response = authenticated_api_client.get(url)

        assert response.status_code == 200
        assert response.data['name'] == test_habit.name

    def test_update_habit(self, authenticated_api_client, test_habit):
        url = reverse('habits:habit-detail', args=[test_habit.id])
        data = {'name': 'Updated Habit'}
        response = authenticated_api_client.patch(url, data)

        assert response.status_code == 200

        test_habit.refresh_from_db()

        assert test_habit.name == 'Updated Habit'

    def test_delete_habit(self, authenticated_api_client, test_habit):
        url = reverse('habits:habit-detail', args=[test_habit.id])
        response = authenticated_api_client.delete(url)

        assert response.status_code == 204
        assert not Habit.objects.filter(id=test_habit.id).exists()


@pytest.mark.django_db
class TestGoalAPI:
    def test_create_goal(self, authenticated_api_client, goal_url, test_habit):
        data = {
            'habit': test_habit.id,
            'target_streak': 10
        }
        response = authenticated_api_client.post(goal_url, data)

        assert response.status_code == 201
        assert Goal.objects.filter(habit=test_habit).exists()

    def test_list_goals(self, authenticated_api_client, goal_url, test_goal):
        response = authenticated_api_client.get(goal_url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['target_streak'] == test_goal.target_streak

    def test_retrieve_goal(self, authenticated_api_client, test_goal):
        url = reverse('habits:goal-detail', args=[test_goal.id])
        response = authenticated_api_client.get(url)

        assert response.status_code == 200
        assert response.data['target_streak'] == test_goal.target_streak

    def test_cannot_update_streak_manually(self, authenticated_api_client, test_goal):
        url = reverse('habits:goal-detail', args=[test_goal.id])
        data = {'current_streak': 5}
        authenticated_api_client.patch(url, data)
        test_goal.refresh_from_db()

        assert test_goal.current_streak == 0

    def test_delete_goal(self, authenticated_api_client, test_goal):
        url = reverse('habits:goal-detail', args=[test_goal.id])
        response = authenticated_api_client.delete(url)

        assert response.status_code == 204
        assert not Goal.objects.filter(id=test_goal.id).exists()


@pytest.mark.django_db
class TestHabitLogAPI:
    def test_create_habit_log(self, authenticated_api_client, habit_log_url, test_habit):
        data = {'habit': test_habit.id}
        response = authenticated_api_client.post(habit_log_url, data)

        assert response.status_code == 201
        assert HabitLog.objects.filter(habit=test_habit).exists()

    def test_create_habit_log_for_own_habit_only(
        self, api_client, habit_log_url, test_habit, test_user_password
    ):
        User = get_user_model()
        another_user = User.objects.create_user(
            email="another_user@example.com",
            password=test_user_password
        )

        api_client.force_authenticate(user=another_user)

        data = {'habit': test_habit.id}
        response = api_client.post(habit_log_url, data)

        assert response.status_code == 400

    def test_create_habit_log_increments_goal_streak(
        self, authenticated_api_client, habit_log_url, test_habit, test_goal
    ):
        initial_streak = test_goal.current_streak
        data = {'habit': test_habit.id}
        response = authenticated_api_client.post(habit_log_url, data)

        assert response.status_code == 201

        test_goal.refresh_from_db()

        assert test_goal.current_streak == initial_streak + 1

    def test_list_habit_logs(self, authenticated_api_client, habit_log_url, test_habit_log):
        response = authenticated_api_client.get(habit_log_url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['habit'] == test_habit_log.habit.id
